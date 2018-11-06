#!/usr/bin/env python3
import yaml
import os

def get_medians_per_segment_of_rpe_type(rpe_type, pipeline_type, dataset_name, results_dir, segments):
    median_list = []
    std_list = []
    with open(os.path.join(results_dir, dataset_name, pipeline_type, "results.yaml"), 'r') as stream:
        try:
            results = yaml.load(stream)
            for segment in segments:
                median_list.append(results['relative_errors'][segment][rpe_type]['median'])
                std_list.append(results['relative_errors'][segment][rpe_type]['std'])
            return median_list, std_list
        except yaml.YAMLError as exc:
            print(exc)

def calculate_mean_of_median_improvement(results_dir, dataset_name, rpe_type):
    # Parse segments file
    with open(os.path.join(results_dir, dataset_name, 'segments.txt'), 'r') as myfile:
        SEGMENTS = myfile.read().replace('\n', '').split(',')

    # Parse list of medians for each segment
    medians_spr, stds_spr = get_medians_per_segment_of_rpe_type(rpe_type, "SPR", dataset_name, results_dir, SEGMENTS)
    medians_sp, stds_sp = get_medians_per_segment_of_rpe_type(rpe_type, "SP", dataset_name, results_dir, SEGMENTS)

    # Output means of median improvements from SP to SPR.
    medians_change = []
    for median_spr, median_sp in zip(medians_spr, medians_sp):
        # Assumes spr is betterr than sp, otherwise we'll get a < 0
        medians_change.append((median_sp - median_spr) / median_sp * 100)

    max_medians_change = max(medians_change)
    mean_of_improvement = sum(medians_change) / float(len(medians_change))

    # Output means of std deviation for SPR and SP
    mean_std_spr = sum(stds_spr) / float(len(stds_spr))
    mean_std_sp = sum(stds_sp) / float(len(stds_sp))

    return mean_of_improvement, max_medians_change, mean_std_spr, mean_std_sp

def write_latex_table():
    start_line = """\\begin{table}[H]
  \\centering
  \\begin{tabularx}{\\textwidth}{l *6{Y}}
    \\toprule
    & \\multicolumn{6}{c}{APE Translation} \\\\
    \\cmidrule{2-7}
    & \\multicolumn{3}{c}{\\textbf{S + P}}  & \\multicolumn{3}{c}{\\textbf{S + P + R} (Proposed)} \\\\
    \\cmidrule(r){2-4} \\cmidrule(l){5-7}
    Sequence & Median (cm) & Mean (cm) & RMSE (cm) & Median (cm) & Mean (cm) & RMSE (cm) \\\\
    \\midrule
    """

    end_line = """
    \\bottomrule
  \\end{tabularx}%
  \\caption{Accuracy of the state estimation when using Structureless factors (S), Structureless and Projection factors (P), and our proposed approach using Structureless, Projection and Regularity factors (R).}
  \\label{tab:accuracy_comparison}
\\end{table}
"""
    bold_in = '& \\textbf{{'
    bold_out = '}} '
    end = '\\\\\n'

    all_lines = start_line

    winners = dict()
    for dataset_name, pipeline_types in sorted(stats.iteritems()):
        median_error_pos = []
        mean_error_pos = []
        rmse_error_pos = []
        for pipeline_type, pipeline_stats in sorted(pipeline_types.iteritems()):
            if pipeline_type is not "S": # Ignore S pipeline
                median_error_pos.append(pipeline_stats["absolute_errors"]["median"])
                mean_error_pos.append(pipeline_stats["absolute_errors"]["mean"])
                rmse_error_pos.append(pipeline_stats["absolute_errors"]["rmse"])

        # Find winning pipeline
        _, median_idx_min = locate_min(median_error_pos)
        _, mean_idx_min = locate_min(mean_error_pos)
        _, rmse_idx_min = locate_min(rmse_error_pos)

        # Store winning pipeline
        winners[dataset_name] = [median_idx_min, mean_idx_min, rmse_idx_min]

    for dataset_name, pipeline_types in sorted(stats.iteritems()):
        start = '{:>25} '.format(dataset_name.replace('_', '\\_'))
        one_line = start
        pipeline_idx = 0
        for pipeline_type, pipeline_stats in sorted(pipeline_types.iteritems()):
            if pipeline_type is not "S": # Ignore S pipeline
                median_error_pos = pipeline_stats["absolute_errors"]["median"] * 100 # as we report in cm
                mean_error_pos = pipeline_stats["absolute_errors"]["mean"] * 100 # as we report in cm
                rmse_error_pos = pipeline_stats["absolute_errors"]["rmse"] * 100 # as we report in cm

                # Bold for min median error
                if len(winners[dataset_name][0]) == 1 and pipeline_idx == winners[dataset_name][0][0]:
                    one_line += bold_in + '{:.1f}'.format(median_error_pos) + bold_out
                else:
                    one_line += '& {:.1f} '.format(median_error_pos)

                # Bold for min mean error
                if len(winners[dataset_name][1]) == 1 and winners[dataset_name][1][0] == pipeline_idx:
                    one_line += bold_in + '{:.1f}'.format(mean_error_pos) + bold_out
                else:
                    one_line += '& {:.1f} '.format(mean_error_pos)

                # Bold for min rmse error
                # Do not bold, if multiple max
                if len(winners[dataset_name][2]) == 1 and winners[dataset_name][2][0] == pipeline_idx:
                    one_line += bold_in + '{:.1f}'.format(rmse_error_pos) + bold_out
                else:
                    one_line += '& {:.1f} '.format(rmse_error_pos)

                pipeline_idx += 1

        one_line += end
        all_lines += one_line
    all_lines += end_line

    # Save table
    results_file = os.path.join(results_dir, 'APE_table.tex')
    print("Saving table of APE results to: " + results_file)
    with open(results_file,'w') as outfile:
        outfile.write(all_lines)

def main():
    results_dir = "/home/tonirv/code/evo/results/"

    datasets = [\
                'MH_01_easy',
                'MH_02_easy',
                'MH_03_medium',
                'mh_04_difficult',
                'MH_05_difficult',
                'V1_01_easy',
                'V1_02_medium',
                'V1_03_difficult',
                'V2_01_easy',
                'V2_02_medium',
                'v2_03_difficult'
               ]
    for dataset_name in datasets:
        print "\033[1m"+dataset_name+"\033[0m"
        mean_of_improvement, max_medians_change, mean_std_spr, mean_std_sp = calculate_mean_of_median_improvement(results_dir, dataset_name, 'rpe_trans')
        print "\tMean of improvement: rpe_trans"
        print mean_of_improvement
        print "\tMax of medians change: rpe_trans"
        print max_medians_change
        mean_of_improvement_rot, max_medians_change_rot, mean_std_spr_rot, mean_std_sp_rot = calculate_mean_of_median_improvement(results_dir, dataset_name, 'rpe_rot')
        print "\tMean of improvement: rpe_rot"
        print mean_of_improvement_rot
        print "\tMax of medians change: rpe_rot"
        print max_medians_change_rot

if __name__ == '__main__':
    main()



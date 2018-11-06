#!/usr/bin/env python

from __future__ import print_function
import copy

print("loading required evo modules")
from evo.core import trajectory, sync, metrics
from evo.tools import file_interface

print("loading trajectories")
traj_ref = file_interface.read_euroc_csv_trajectory("../../results/MH_01_easy/S/traj_gt.csv")
traj_est = file_interface.read_swe_csv_trajectory("../../results/MH_01_easy/S/traj_es.csv")

print("registering and aligning trajectories")
traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est)
traj_est = trajectory.align_trajectory(traj_est, traj_ref, correct_scale=False)

print("calculating APE translation part")
data = (traj_ref, traj_est)
ape_metric = metrics.APE(metrics.PoseRelation.translation_part)
ape_metric.process_data(data)
ape_statistics = ape_metric.get_all_statistics()
print(ape_statistics)
print("mean:", ape_statistics["mean"])

print("calculating RPE translation part")
rpe_metric_trans = metrics.RPE(metrics.PoseRelation.translation_part,
                         1.0, metrics.Unit.frames, 1.0, True)
rpe_metric_trans.process_data(data)
rpe_stats_trans = rpe_metric_trans.get_all_statistics()
print(rpe_stats_trans)
print("mean:", rpe_stats_trans["mean"])

print("calculating RPE rotation angle")
rpe_metric_rot = metrics.RPE(metrics.PoseRelation.rotation_angle_deg,
                             1.0, metrics.Unit.frames, 1.0, False)
rpe_metric_rot.process_data(data)
rpe_stats_rot = rpe_metric_rot.get_all_statistics()
print(rpe_stats_rot)
print("mean:", rpe_stats_rot["mean"])

print("loading plot modules")
from evo.tools import plot
import matplotlib.pyplot as plt

print("plotting")
plot_collection = plot.PlotCollection("Example")
# metric values
fig_1 = plt.figure(figsize=(8, 8))
plot.error_array(fig_1, ape_metric.error, statistics=ape_statistics,
                 name="APE", title=str(ape_metric))
plot_collection.add_figure("raw ape trans", fig_1)

# trajectory colormapped with error
fig_2 = plt.figure(figsize=(8, 8))
plot_mode = plot.PlotMode.xy
ax = plot.prepare_axis(fig_2, plot_mode)
plot.traj(ax, plot_mode, traj_ref, '--', 'gray', 'reference')
plot.traj_colormap(ax, traj_est, ape_metric.error, plot_mode,
                   min_map=ape_statistics["min"], max_map=ape_statistics["max"],
                   title="APE mapped onto trajectory")
plot_collection.add_figure("ape trans traj (error)", fig_2)

# RPE
## Trans
### metric values
fig_3 = plt.figure(figsize=(8, 8))
plot.error_array(fig_3, rpe_metric_trans.error, statistics=rpe_stats_trans,
                 name="RPE trans error", title=str(rpe_metric_trans))
plot_collection.add_figure("raw rpe trans", fig_3)

### trajectory colormapped with error
fig_4 = plt.figure(figsize=(8, 8))
plot_mode = plot.PlotMode.xy
ax = plot.prepare_axis(fig_4, plot_mode)
traj_ref_trans = copy.deepcopy(traj_ref)
traj_ref_trans.reduce_to_ids(rpe_metric_trans.delta_ids)
traj_est_trans = copy.deepcopy(traj_est)
traj_est_trans.reduce_to_ids(rpe_metric_trans.delta_ids)
plot.traj(ax, plot_mode, traj_ref_trans, '--', 'gray', 'reference')
plot.traj_colormap(ax, traj_est_trans, rpe_metric_trans.error, plot_mode,
                   min_map=rpe_stats_trans["min"], max_map=rpe_stats_trans["max"],
                   title="RPE trans mapped onto trajectory")
plot_collection.add_figure("rpe trans traj (error)", fig_4)

## Rot
### metric values
fig_5 = plt.figure(figsize=(8, 8))
plot.error_array(fig_5, rpe_metric_rot.error, statistics=rpe_stats_rot,
                 name="RPE rot error", title=str(rpe_metric_rot))
plot_collection.add_figure("raw rpe rot", fig_5)

### trajectory colormapped with error
fig_6 = plt.figure(figsize=(8, 8))
plot_mode = plot.PlotMode.xy
ax = plot.prepare_axis(fig_6, plot_mode)
traj_ref_rot = copy.deepcopy(traj_ref)
traj_ref_rot.reduce_to_ids(rpe_metric_rot.delta_ids)
traj_est_rot = copy.deepcopy(traj_est)
traj_est_rot.reduce_to_ids(rpe_metric_rot.delta_ids)
plot.traj(ax, plot_mode, traj_ref_rot, '--', 'gray', 'reference')
plot.traj_colormap(ax, traj_est_rot, rpe_metric_rot.error, plot_mode,
                   min_map=rpe_stats_rot["min"], max_map=rpe_stats_rot["max"],
                   title="RPE rot mapped onto trajectory")
plot_collection.add_figure("rpe rot traj (error)", fig_6)

# trajectory colormapped with speed
# fig_3 = plt.figure(figsize=(8, 8))
# plot_mode = plot.PlotMode.xy
# ax = plot.prepare_axis(fig_3, plot_mode)
# speeds = [trajectory.calc_speed(traj_est.positions_xyz[i], traj_est.positions_xyz[i + 1],
                    # traj_est.timestamps[i], traj_est.timestamps[i + 1])
                    # for i in range(len(traj_est.positions_xyz) - 1)]
# speeds.append(0)
# plot.traj(ax, plot_mode, traj_ref, '--', 'gray', 'reference')
# plot.traj_colormap(ax, traj_est, speeds, plot_mode,
                   # min_map=min(speeds), max_map=max(speeds),
                   # title="speed mapped onto trajectory")
# fig_3.axes.append(ax)
# plot_collection.add_figure("traj (speed)", fig_3)

plot_collection.show()
plot_collection.export("./save_plot", True)

"""
This module simulates a 6 degree-of-freedom dynamic quadrotor model as it seeks
to reach a goal region while avoiding dynamic obstacles.

"""

from typing import List
from jax import Array
import numpy as np
import cbfkit.system as system
from cbfkit.models import fixed_wing_uav
from cbfkit.sensors import perfect as sensor
from cbfkit.estimators import naive as estimator
from cbfkit.integration import forward_euler as integrator
from cbfkit.controllers.model_based.cbf_clf_controllers.cbf_clf_qp_controllers import (
    cbf_clf_controller,
)
from examples.fixed_wing.reach_drop_point.ra_fxt_clbf.perfect_state_measurements import setup

from examples.fixed_wing.reach_drop_point.ra_fxt_clbf.lyapunov_barrier_functions import (
    fxts_lyapunov_barrier_vel_and_obs,
    # fxts_lyapunov_barrier_velpos,
)

# from examples.fixed_wing.reach_drop_point.ra_fxt_clbf.barrier_functions import obstacle_ff_barriers
# from examples.fixed_wing.reach_drop_point.ra_fxt_clbf.lyapunov_functions import fxts_lyapunovs_vel

# Lyapunov Barrier Functions
lyapunovs = fxts_lyapunov_barrier_vel_and_obs(
    setup.desired_velpos,
    setup.goal_radius,
    setup.obstacle_locations,
    setup.ellipsoid_radii,
    setup.alpha,
    setup.c1,
    setup.c2,
    setup.e1,
    setup.e2,
)
# lyapunovs = fxts_lyapunov_barrier_velpos(
#     setup.desired_state,
#     setup.goal_radius,
#     setup.obstacle_locations,
#     setup.ellipsoid_radii,
#     setup.c1,
#     setup.c2,
#     setup.e1,
#     setup.e2,
# )

# lyapunovs = fxts_lyapunovs_vel(
#     setup.desired_state,
#     setup.goal_radius,
#     setup.c1,
#     setup.c2,
#     setup.e1,
#     setup.e2,
# )
# barriers = obstacle_ff_barriers(
#     setup.obstacle_locations,
#     setup.obstacle_radii,
#     setup.lookahead_time,
# )

# number of simulation steps
N_STEPS = int(setup.tf / setup.dt)

# Define dynamics, controller, and estimator with specified parameters
dynamics = fixed_wing_uav.fixed_wing_uav_kinematics()
nominal_controller = fixed_wing_uav.zero_controller()

controller = cbf_clf_controller(
    nominal_input=nominal_controller,
    dynamics_func=dynamics,
    # barriers=barriers,
    lyapunovs=lyapunovs,
    control_limits=setup.actuation_limits,
    alpha=np.array([0.1]),
    R=setup.QP_J,
)


def execute(_ii: int = 1) -> List[Array]:
    """_summary_

    Args:
        int (ii): _description_

    Returns:
        List[Array]: _description_
    """
    x, u, z, p, dkeys, dvalues = system.execute(
        x0=setup.initial_state,
        dynamics=dynamics,
        sensor=sensor,
        controller=controller,
        estimator=estimator,
        integrator=integrator,
        dt=setup.dt,
        R=setup.R,
        num_steps=N_STEPS,
    )

    # Reformat results as numpy arrays
    x = np.array(x)
    u = np.array(u)
    z = np.array(z)
    p = np.array(p)

    return x, u, z, p, dkeys, dvalues


# if SIMULATE:
#     # Execute simulation
#     states, controls, estimates, covariances, data_keys, data_values = system.execute(
#         x0=setup.initial_state,
#         dynamics=dynamics,
#         sensor=sensor,
#         controller=controller,
#         estimator=estimator,
#         integrator=integrator,
#         dt=setup.dt,
#         R=setup.R,
#         num_steps=N_STEPS,
#     )

#     # Reformat results as numpy arrays
#     states = np.array(states)
#     controls = np.array(controls)
#     estimates = np.array(estimates)
#     covariances = np.array(covariances)

#     print(states[-1])

# else:
#     # Implement load from file
#     pass

states, controls, estimates, covariances, data_keys, data_values = execute()

from examples.fixed_wing.reach_drop_point.visualizations.animate_2d_path import (
    animate as animate_2d,
)

from examples.fixed_wing.reach_drop_point.visualizations.path_3d import animate as animate_3d

animate_3d(
    trajectory=states, obstacles=setup.obstacle_locations, r_obs=setup.ellipsoid_radii, dt=setup.dt
)
animate_2d(
    states=states,
    estimates=estimates,
    desired_state=setup.desired_state,
    desired_state_radius=0.1,
    obstacles=setup.obstacle_locations,
    r_obs=setup.ellipsoid_radii,
    x_lim=(-100, 1000),
    y_lim=(-100, 500),
    dt=setup.dt,
    title="System Behavior",
    save_animation=False,
    animation_filename="examples/fixed_wing/start_to_goal/ra_fxt_clbf/perfect_state_measurements/results/test",
)
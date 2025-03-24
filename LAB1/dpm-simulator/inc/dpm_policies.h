/**
 * @file dpm_policies.h
 * @brief Functions related to dynamic power management policies
 */

#ifndef _INCLUDE_DPM_POLICIES_H
#define _INCLUDE_DPM_POLICIES_H

#include "inc/psm.h"

/**
 * @defgroup dpm_params Parameters of DPM policies
 * @{
 */
/** history window size for history-based policies */
#define DPM_HIST_WIND_SIZE 2
/** number of thresholds for history-based policies */
#define DPM_N_THRESHOLDS 2
/** @} */

/**
 * @defgroup simulator_params Parameters of the DPM simulator
 * @{
 */
/** simulation time granularity (in seconds) **/
#define SIMULATION_TIME_STEP 1e-4
/** @} */

/**
 * @defgroup dpm_policy_ids DPM policy identifiers
 * @{
 */
/** timeout-based policy */
#define DPM_TIMEOUT_IDLE 0
#define DPM_TIMEOUT_SLEEP 1
/** history-based policy */
#define DPM_HISTORY 2
#define DPM_HISTORY_A 3
#define DPM_HISTORY_I 4
#define DPM_HISTORY_EXP 5
#define DPM_ORACLE 6
/** @} */

/** Type alias for DPM policy IDs */
typedef int dpm_policy_t;

/**
 * @brief Container for timeout policy parameters (can store more than 1 timeout)
 */
typedef struct {
    /* Day2: you can add/change stuff here */
    psm_time_t timeout;
} dpm_timeout_params;

/**
 * @brief Container for history policy parameters
 *
 */
typedef struct {
    /* Day3: you can add/change stuff here */
    double alpha[DPM_HIST_WIND_SIZE]; /**< regression model coefficients */
    psm_time_t threshold[DPM_N_THRESHOLDS]; /**< thresholds on the predicted time that trigger a state transition */
    psm_time_t g_next_arrival;
} dpm_history_params;

/**
 * @brief Container for workload requests, i.e., items of work to be done
 * by the simulated system, each with a request time (arrival) and a duration
 *
 */
typedef struct{
    psm_time_t duration;
    psm_time_t arrival;
} dpm_work_item;

/**
 * @brief Run the DPM simulation loop on a workload file
 *
 * @param psm: the input psm specification
 * @param sel_policy: the selected policy type
 * @param tparams: the timeout policy parameters (if selected)
 * @param hparams: the history policy parameters (if selected)
 * @param fwl: the worload filename
 *
 * @return 1 on success, 0 on failure
 *
 */
int dpm_simulate(psm_t psm, dpm_policy_t sel_policy, dpm_timeout_params
        tparams, dpm_history_params hparams, char* fwl);

/**
 * @brief Initialize the work queue using data from a workload file
 *
 * @param num_items: pointer to an integer that will be filled with the
 * number of work items in the queue
 * @param fwl: the input filename
 *
 * @return a pointer to a dynamically allocated array of dpm_work_item elements.
 *
 */
dpm_work_item* dpm_init_work_queue(int *num_items, char *fwl);

/**
 * @brief Decide the next PSM state according to a given DPM policy
 *
 * @param next_state: will be filled with the selected next state
 * @param prev_state: the previous PSM state (not needed right now, but could be useful)
 * @param t_curr: the current time instant
 * @param t_inactive_start: the time instant in which the system became inactive
 * @param history: the history of previous inactive intervals durations (used for
 * history policies)
 * @param policy: the ID of the selected DPM policy
 * @param tparams: the parameters of the timeout policy (if selected)
 * @param hparams: the parameters of the history policy (if selected)
 *
 * @return 1 on success, 0 on failure
 *
 */
int dpm_decide_state(psm_state_t *next_state, psm_state_t prev_state, psm_time_t t_curr,
        psm_time_t t_inactive_start, psm_time_t *history, psm_time_t *t_last_pred, dpm_policy_t policy,
        dpm_timeout_params tparams, dpm_history_params hparams, psm_time_t g_next_arrival);

/**
 * @brief Initialize the history of previous inactive times at the beginning of a simulation
 *
 * @param h: the array containing the history of inactive intervals
 *
 */
void dpm_init_history(psm_time_t *h);

/**
 * @brief Update the history of previous inactive times
 *
 * @param h: the array containing the history of inactive intervals
 * @param new_inactive: the new inactive interval to be inserted
 *
 */
void dpm_update_history(psm_time_t *h, psm_time_t new_inactive);

/**
 * @brief Update the history of previous inactive times
 *
 * @param hparams: the parameters of the history policy (if selected)
 * @param history: the history of previous inactive intervals durations (used for
 * history policies)
 * @param t_last_pred: the last predicted inactive time (used in the formula of predictive exponential policy)
 *
 */
void exp_pred(dpm_history_params hparams, psm_time_t *history, psm_time_t *t_last_pred);

#endif

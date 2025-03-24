/**
 * @file psm.h
 * @brief Functions related to power state machines
 */

#ifndef _INCLUDE_PSM_H
#define _INCLUDE_PSM_H

#include <stdlib.h>
#include <stdio.h>

/**
 * @brief Number of states in the PSM
 */
#define PSM_N_STATES 3

/**
 * @defgroup psm_unit Units of measure in the PSM
 * @{
 */
/** time unit */
#define PSM_TIME_UNIT   1e-03
/** power unit */
#define PSM_POWER_UNIT  1e-03
/** energy unit */
#define PSM_ENERGY_UNIT 1e-03
/** @} */

/**
 * @defgroup psm_state PSM state IDs
 * @{
 */
/** active state */
#define PSM_STATE_RUN 0
/** idle state */
#define PSM_STATE_IDLE   1
/** sleep state */
#define PSM_STATE_SLEEP  2
/** @} */

/**
 * @defgroup psm_type PSM type aliases
 * @{
 */
/** type for PSM states */
typedef int psm_state_t;
/** type for time variables */
typedef double psm_time_t;
/** type for energy variables */
typedef double psm_energy_t;
/** type for power variables */
typedef double psm_power_t;
/** @} */


/**
 * A (bad) macro to convert state IDs to names
 */
#define PSM_STATE_NAME(val) (val == PSM_STATE_RUN ? "Run" : (val == PSM_STATE_IDLE ? "Idle" : "Sleep" ))

/**
 * @brief Container for power state machine parameters
 */
typedef struct {
    psm_power_t  power[PSM_N_STATES]; /**< power in the different states */
    psm_energy_t tran_energy[PSM_N_STATES][PSM_N_STATES]; /**< transition energy */
    psm_time_t   tran_time[PSM_N_STATES][PSM_N_STATES]; /**< transition time */
} psm_t;

/**
 * @brief Read a file containing power state machine specifications and fill a data structure accordingly
 *
 * @param p: destination container
 * @param filename: name of the file to read
 *
 * @return 1 on success, 0 on failure
 *
 */
int psm_read(psm_t *p, char *filename);

/**
 * @brief Print a psm specification from a container structure
 *
 * @param p: source container
 *
 */
void psm_print(psm_t p);

/**
 * @brief Check if a transition between two states is allowed or not in a psm specification
 *
 * @param psm: the power state machine specification
 * @param curr: the source psm state
 * @param next: the target psm state
 *
 * @return 1 if the transition is allowed, 0 otherwise
 *
 */
int psm_tran_allowed(psm_t psm, psm_state_t curr, psm_state_t next);

/**
 * @brief Compute transition energy when moving from a psm state to another
 *
 * @param psm: the power state machine specification
 * @param curr: the source psm state
 * @param next: the target psm state
 *
 * @return the transition energy
 *
 */
psm_energy_t psm_tran_energy(psm_t psm, psm_state_t curr, psm_state_t next);

/**
 * @brief Compute transition time when moving from a psm state to another
 *
 * @param psm: the power state machine specification
 * @param curr: the source psm state
 * @param next: the target psm state
 *
 * @return the transition time
 *
 */
psm_time_t psm_tran_time(psm_t psm, psm_state_t curr, psm_state_t next);

/**
 * @brief Compute energy consumed while staying in a given psm state for a given time
 *
 * @param psm: the power state machine specification
 * @param curr: the current psm state
 * @param time: the time spent in the state
 *
 * @return the energy consumed
 *
 */
psm_energy_t psm_state_energy(psm_t psm, psm_state_t curr, psm_time_t time);

#endif

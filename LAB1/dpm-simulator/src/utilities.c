#include "inc/utilities.h"

int parse_args(int argc, char *argv[], char *fwl, psm_t *psm, dpm_policy_t
        *selected_policy, dpm_timeout_params *tparams, dpm_history_params
        *hparams)
{
    int cur = 1;
    while(cur < argc) {

        if(strcmp(argv[cur], "-help") == 0) {
            print_command_line();
            return 0;
        }

        // set policy to timeout and get timeout value
        if(strcmp(argv[cur], "-ti") == 0) {
            *selected_policy = DPM_TIMEOUT_IDLE;
            if(argc > cur + 1) {
                tparams->timeout = atof(argv[++cur]);
            }
            else return	0;
        }

        // set policy to timeout and get timeout value
        if(strcmp(argv[cur], "-ts") == 0) {
            *selected_policy = DPM_TIMEOUT_SLEEP;
            if(argc > cur + 1) {
                tparams->timeout = atof(argv[++cur]);
            }
            else return	0;
        }

        // set policy to history based and get parameters and thresholds
        if(strcmp(argv[cur], "-h") == 0) {
            *selected_policy = DPM_HISTORY;
            if(argc > cur + DPM_HIST_WIND_SIZE + 2){
                int i;
                for(i = 0; i < DPM_HIST_WIND_SIZE; i++) {
                    hparams->alpha[i] = atof(argv[++cur]);
                }
                hparams->threshold[0] = atof(argv[++cur]);
                hparams->threshold[1] = atof(argv[++cur]);
            } else return 0;
        }
        
        // set policy to history based on prevoius active time
        if(strcmp(argv[cur], "-ha") == 0) {
            *selected_policy = DPM_HISTORY_A;
            if(argc > cur + DPM_HIST_WIND_SIZE + 2){
                hparams->threshold[0] = atof(argv[++cur]);
                hparams->threshold[1] = atof(argv[++cur]);
            } else return 0;
        }

        // set policy to history based on prevoius inactive time
        if(strcmp(argv[cur], "-hi") == 0) {
            *selected_policy = DPM_HISTORY_I;
            if(argc > cur + DPM_HIST_WIND_SIZE + 2){
                hparams->threshold[0] = atof(argv[++cur]);
                hparams->threshold[1] = atof(argv[++cur]);
            } else return 0;
        }

        // set policy to history based on prevoius inactive time
        if(strcmp(argv[cur], "-he") == 0) {
            *selected_policy = DPM_HISTORY_EXP;
            if(argc > cur + DPM_HIST_WIND_SIZE + 2){
                hparams->alpha[0] = atof(argv[++cur]);
                hparams->threshold[0] = atof(argv[++cur]);
                hparams->threshold[1] = atof(argv[++cur]);
            } else return 0;
        }

        // set policy based on oracle
        if(strcmp(argv[cur], "-or") == 0) {
            *selected_policy = DPM_ORACLE;
        }

        // set name of file for the power state machine
        if(strcmp(argv[cur], "-psm") == 0) {
            if(argc <= cur + 1 || !psm_read(psm, argv[++cur]))
                return 0;
        }

        // set name of file for the workload
        if(strcmp(argv[cur], "-wl") == 0)
        {
            if(argc > cur + 1)
            {
                strcpy(fwl, argv[++cur]);
            }
            else return	0;
        }
        cur ++;
    }
    return 1;
}

void print_command_line(){
	printf("\n******************************************************************************\n");
	printf(" DPM simulator: \n");
	printf("\t-ti <timeout>: timeout of the timeout policy for idle state\n");
    printf("\t-ts <timeout>: timeout of the timeout policy for sleep state\n");
	printf("\t-h <Value1> …<Value5> <Threshold1> <Threshold2>: history-based policy \n");
	printf("\t   <Value1-5> value of coefficients\n");
	printf("\t   <Threshold1-2> predicted time thresholds\n");
    printf("\t-ha <Idle Threshold> <Sleep Threshold>: history-based on last active time policy \n");
    printf("\t-hi <Idle Threshold> <Sleep Threshold>: history-based on last incative time policy \n");
	printf("\t   <Threshold Idle-Sleep> predicted time thresholds\n");
    printf("\t-he <Alpha value><Idle Threshold> <Sleep Threshold>: history-based exponential average Tpred = (alpha * Tidle-1) + (1-alpa)Tpred-1 \n");
    printf("\t   <Alpha> 0 => recent history has no effect, 1 => last prediction has no effect\n");
	printf("\t   <Threshold Idle-Sleep> predicted time thresholds\n");
	printf("\t-psm <psm filename>: the power state machine file\n");
	printf("\t-wl <wl filename>: the workload file\n");
	printf("******************************************************************************\n\n");
}

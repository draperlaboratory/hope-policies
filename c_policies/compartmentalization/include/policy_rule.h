#ifndef POLICY_RULE_H
#define POLICY_RULE_H

#include "policy_eval.h"
#include "comp_ht.h"


#define POLICY_EXP_FAILURE 0
#define POLICY_IMP_FAILURE -1
#define POLICY_SUCCESS 1

#define DEBUG_STUFF 0
#ifdef __cplusplus
extern "C" {
#endif

void logRuleInit();
void logRuleEval(const char* ruleDescription);
const char* nextLogRule(int* idx);
void load_inital_CAPMAP();
void set_max_subjs_objs();
  
#ifdef __cplusplus
}
#endif

#endif // POLICY_RULE_H

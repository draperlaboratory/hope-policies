/* RIPE was originally developed by John Wilander (@johnwilander)
 * and was debugged and extended by Nick Nikiforakis (@nicknikiforakis)
 *
 * RISC-V port developed by John Merrill
 *
 * Released under the MIT license (see file named LICENSE)
 *
 * This program is part the paper titled
 * RIPE: Runtime Intrusion Prevention Evaluator 
 * Authored by: John Wilander, Nick Nikiforakis, Yves Younan,
 *              Mariam Kamkar and Wouter Joosen
 * Published in the proceedings of ACSAC 2011, Orlando, Florida
 *
 * Please cite accordingly.
 */

/**
 * @author John Wilander
 * 2007-01-16
 */

#ifndef RIPE_PARAMETERS_H
#define RIPE_PARAMETERS_H

#define ATTACK_IMPOSSIBLE -900
#define ATTACK_NOT_IMPLEMENTED -909

#include <stdbool.h>

#include "ripe_types.h"

void set_technique(char *choice, ripe_attack_form_t *attack);
void set_inject_param(char *choice, ripe_attack_form_t *attack);
void set_code_ptr(char *choice, ripe_attack_form_t *attack);
void set_location(char *choice, ripe_attack_form_t *attack);
void set_function(char *choice, ripe_attack_form_t *attack);
bool is_attack_possible(ripe_attack_form_t attack);

#endif // RIPE_PARAMETERS_H

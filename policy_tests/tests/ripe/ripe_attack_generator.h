/* RIPE was originally developed by John Wilander (@johnwilander)
 * and was debugged and extended by Nick Nikiforakis (@nicknikiforakis)
 *
 * The RISC-V port of RIPE was developed by John Merrill.
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

#ifndef RIPE_ATTACK_GENERATOR_H
#define RIPE_ATTACK_GENERATOR_H

#include <stdbool.h>
#include <setjmp.h>

#include "ripe_types.h"

int ripe_main(void);

STACK_PARAMETER_FUNCTION(void, perform_attack, 
                         int (*stack_func_ptr_param)(const char *),
                         jmp_buf stack_jmp_buffer_param);

#endif // RIPE_ATTACK_GENERATOR_H

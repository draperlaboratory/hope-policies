/* this version of the STANFORD COMPOSITE is taken from "Performance Report -
Motorola's 68020 & 68030 32-bit Microprocessors", Motorola Publication
BR705/D, 1988, pgs. A2-1,A2-15 */

/* this is a suite of benchmarks that are relatively short, both in program
size and execution time. it requires no input, and prints the execution
time for each program, using the system-dependent Getclock, below, to find
out the current CPU time. it does a rudimentary check to make sure each
program gets the right output. 

these programs were gathered by John Hennessy and modified by Peter Nye. */

// this version contains only the "treesort" benchmark

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "test_status.h"


//#define DEBUG 1

#define nil             0
#define false           0
#define true            1

// the data size for treesort is (24+4) = 28 bytes per data element
// thus, for an ~8 KB data area, set the sortelements = 291
#define sortelements    200 // note -- increasing this risks failure on sifive-e

// number of times to run the sort test
#define ITERATIONS      2

/* tree */
struct node {
    struct node *left, *right;
    int32_t val;
};
  
/* tree */
struct  node *tree;

/* bubble, quick, tree sorts */
int32_t sortlist[sortelements+1],
        biggest,
        littlest;

/* GLOBAL */
int32_t     seed;
int32_t     lfsr;

// 32-bit LFSR CRC
#define POLYNOMIAL      0xb4bcd35cL  // ethernet crc-32
#define LFSR_INIT       0xbabefaceL  // 32-bit (x^32 + ...)

/* GLOBAL PROCEDURES */

Initrand ()
{
        seed = LFSR_INIT;
        lfsr = LFSR_INIT;
}

int32_t Rand ()
{
    int32_t i;

/* simple calculation of next "random" number
    seed = (seed * 1309 + 13849) & 65535;
    return (seed);
*/
    i = lfsr & 1L;      // get LSB
    lfsr >>= 1L;        // perform shift
    if (i == 1L) {
        lfsr ^= POLYNOMIAL;
    }

    return (lfsr);
}

/*****************************************************************************/
/*****************************************************************************/

/* SORTS AN ARRAY USING TREESORT */

Initarr ()
{
    int32_t     i;

    Initrand ();
    biggest = -32768;
    littlest = 32767;
    for (i = 1; i <= sortelements; i++)
    {
        seed = Rand(); 
        sortlist[i] = seed;
        if (sortlist[i] > biggest) biggest = sortlist[i];
            else if ( sortlist[i] < littlest) littlest = sortlist[i];
#ifdef  DEBUG
        t_printf("sortlist[%.4d] = %.8x\n", i, sortlist[i]);
#endif  // DEBUG
    };
#ifdef  DEBUG
        t_printf("littlest = %.8x, biggest = %.8x\n", littlest, biggest);
#endif  // DEBUG
}

CreateNode (t,n)
    struct  node **t;
    int32_t n;
{
//    *t = (struct node *) simple_malloc (sizeof(struct node));
    *t = (struct node *) malloc (sizeof(struct node));
      if(!tree)
        t_printf("ERROR: Out of memory\n");
#ifdef  DEBUG
    t_printf ("malloc call = %d\n", (sizeof(struct node)));
#endif  // DEBUG
    (*t)->left  = nil;
    (*t)->right = nil;
    (*t)->val   = n;
}

Insert (n,t)
    int32_t n;
    struct node *t;

{
    /* insert n into tree */
    if (n > t->val)
        if (t->left == nil)
                CreateNode (&t->left, n);
        else Insert (n,t->left);
    else if (n < t->val)
        if (t->right == nil)
                CreateNode (&t->right, n);
        else Insert (n,t->right);
}

int32_t Checktree (p)
    struct node *p;

{
    /* check by in-order tranversal */
    int32_t result;

    result = true;
    if (p->left != nil)
        if (p->left->val <= p->val)
                result = false;
        else result = Checktree (p->left) && result;
    if (p->right != nil)
        if (p->right->val >= p->val)
                result = false;
        else result = Checktree (p->right) && result;
    return (result);
}

void Prune (p)
    struct node *p;

{
    /* recursively free all nodes below this one */

  if (p->left != nil){
    Prune(p->left);
    free(p->left);
  }
  if (p->right != nil){
    Prune(p->right);
    free(p->right);
  }

}

Trees ()
{
    int32_t i;
    Initarr();
//    tree = (struct node *) simple_malloc (sizeof(struct node));
    tree = (struct node *) malloc (sizeof(struct node));
#ifdef  DEBUG
    t_printf ("malloc call = %d\n", (sizeof(struct node)));
#endif  // DEBUG
    tree->left  = nil;
    tree->right = nil;
    tree->val   = sortlist[1];

    for (i = 2; i <= sortelements; i++)
            Insert (sortlist[i], tree);

    if (!Checktree(tree))
            t_printf ("Error in Tree\n");
    /* Free inserted memory */
    Prune(tree);
    /* free the root node */
    free(tree);
}

int test_main (void)
{
  test_positive(); // identify test as positive (will complete)

#ifdef  DEBUG
  t_printf ("TREE\n");
#endif  // DEBUG

  for(int i= 0; i < ITERATIONS;i++){
    Trees();
  }

    // code to force violations
    /*
    uintptr_t *ptr = (uintptr_t*) main;
    ptr[0] = 0;
    */

  test_pass();
  return test_done();

}

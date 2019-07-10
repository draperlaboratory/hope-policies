#include <stdlib.h>
#include <stdio.h>
#include "input.h"

#include "test_status.h"
#include "test.h"

#ifndef NUM_NODES
#define NUM_NODES                          100
#endif
#define NONE                               9999

struct _NODE
{
  int iDist;
  int iPrev;
};
typedef struct _NODE NODE;

struct _QITEM
{
  int iNode;
  int iDist;
  int iPrev;
  struct _QITEM *qNext;
};
typedef struct _QITEM QITEM;

QITEM allocated[100];
QITEM *qHead = NULL;

int g_qCount = 0;
NODE rgnNodes[NUM_NODES];
int ch;
int iPrev, iNode;
int i, iCost, iDist;


void print_path (NODE *rgnNodes, int chNode)
{
  if (rgnNodes[chNode].iPrev != NONE)
    {
      print_path(rgnNodes, rgnNodes[chNode].iPrev);
    }
  //t_printf (" %d", chNode);
  fflush(stdout);
}

void enqueue (int iNode, int iDist, int iPrev)
{
  static int notAll = 0;
  QITEM *qNew = &allocated[notAll];
  notAll++;
  QITEM *qLast = qHead;
  
  if (!qNew) 
    {
      test_error("Out of memory.\n");
      exit(1);
    }
  qNew->iNode = iNode;
  qNew->iDist = iDist;
  qNew->iPrev = iPrev;
  qNew->qNext = NULL;
  
  if (!qLast) 
    {
      qHead = qNew;
    }
  else
    {
      qLast = &allocated[notAll-2];
      qLast->qNext = qNew;
    }
  g_qCount++;
  //               ASSERT(g_qCount);
}


void dequeue (int *piNode, int *piDist, int *piPrev)
{
  QITEM *qKill = qHead;
  
  if (qHead)
    {
      //                 ASSERT(g_qCount);
      *piNode = qHead->iNode;
      *piDist = qHead->iDist;
      *piPrev = qHead->iPrev;
      qHead = qHead->qNext;
      //free(qKill);
      g_qCount--;
    }
}


int qcount (void)
{
  return(g_qCount);
}

int dijkstra(int chStart, int chEnd) 
{
  

  for (ch = 0; ch < NUM_NODES; ch++)
    {
      rgnNodes[ch].iDist = NONE;
      rgnNodes[ch].iPrev = NONE;
    }
  if (chStart == chEnd) 
    {
      //t_printf("Shortest path is 0 in cost. Just stay where you are.\n");
    }
  else
    {
      rgnNodes[chStart].iDist = 0;
      rgnNodes[chStart].iPrev = NONE;
      enqueue (chStart, 0, NONE);

     while (qcount() > 0)
	{
	  dequeue (&iNode, &iDist, &iPrev);
	  for (i = 0; i < NUM_NODES; i++)
	    {
	      if ((iCost = AdjMatrix[iNode][i]) != NONE)
		{
		  if ((NONE == rgnNodes[i].iDist) || 
		      (rgnNodes[i].iDist > (iCost + iDist)))
		    {
		      rgnNodes[i].iDist = iDist + iCost;
		      rgnNodes[i].iPrev = iNode;
		      enqueue (i, iDist + iCost, iNode);
		    }
		}
	    }
	}
      
      t_printf("Shortest path is %d in cost. ", rgnNodes[chEnd].iDist);
      //t_printf("Path is: ");
      //t_print_path(rgnNodes, chEnd);
      t_printf("\n");
    }
    return 0;
}

int test_main(void) {
  int i,j;

  test_positive();
  test_begin();
  test_start_timer();

   /* make a fully connected matrix */
   // see input.h
  /* finds 10 shortest paths between nodes */
  for (i=0,j=NUM_NODES/2;i<NUM_NODES;i++,j++) {
			j=j%NUM_NODES;
      dijkstra(i,j);
  }

  test_print_total_time();
  return test_done();
}

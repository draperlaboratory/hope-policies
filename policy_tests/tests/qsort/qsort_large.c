#include <stdlib.h>
#include <math.h>
#include "input_large.h"
#include "test_status.h"
#include "test.h"

#define UNLIMIT


/*struct my3DVertexStruct {
  int x, y, z;
  double distance;
};*/

int compare(const void *elem1, const void *elem2)
{
  /* D = [(x1 - x2)^2 + (y1 - y2)^2 + (z1 - z2)^2]^(1/2) */
  /* sort based on distances from the origin... */

  double distance1, distance2;

  distance1 = (*((struct my3DVertexStruct *)elem1)).distance;
  distance2 = (*((struct my3DVertexStruct *)elem2)).distance;

  return (distance1 > distance2) ? 1 : ((distance1 == distance2) ? 0 : -1);
}

int test_main(void)
{
  int i,count=0;

  test_positive();
  test_begin();
  test_start_timer();

  for(count = 0; count < sizeof(array)/sizeof(struct my3DVertexStruct); ++count)
	 array[count].distance = sqrt(pow(array[count].x, 2) + pow(array[count].y, 2) + pow(array[count].z, 2));
  
  t_printf("\nSorting %d vectors based on distance from the origin.\n\n",count);
  qsort(array,count,sizeof(struct my3DVertexStruct),compare);
  
  for(i = 0; i < 10; ++i)
  {
    t_printf("%d %d %d\n", array[i].x, array[i].y, array[i].z);
  }
  t_printf("...\n");
  for(i = count - 10; i < count; ++i)
  {
    t_printf("%d %d %d\n", array[i].x, array[i].y, array[i].z);
  }

  test_print_total_time();
  return test_done();
}

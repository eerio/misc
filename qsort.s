/* print-array.s */
 
.data
 
/* declare an array of 10 integers called my_array */
.align 4
my_array: .word 82, 70, 93, 77, 91, 30, 42, 6, 92, 64
 
/* format strings for printf */
/* format string that prints an integer plus a space */
.align 4
integer_printf: .asciz "%d "
/* format string that simply prints a newline */
.align 4
newline_printf: .asciz "\n"
 
.text
 
print_array:
    /* r0 will be the address of the integer array */
    /* r1 will be the number of items in the array */
    push {r4, r5, r6, lr}  /* keep r4, r5, r6 and lr in the stack */
 
    mov r4, r0             /* r4 ← r0. keep the address of the array */
    mov r5, r1             /* r5 ← r1. keep the number of items */
    mov r6, #0             /* r6 ← 0.  current item to print */
 
    b .Lprint_array_check_loop /* go to the condition check of the loop */
 
    .Lprint_array_loop:
      /* prepare the call to printf */
      ldr r0, addr_of_integer_printf  /* r0 ← &integer_printf */
      /* load the item r6 in the array in address r4.
         elements are of size 4 bytes so we need to multiply r6 by 4 */
      ldr r1, [r4, +r6, LSL #2]       /* r1 ← *(r4 + r6 << 2)
                                         this is the same as
                                         r1 ← *(r4 + r6 * 4) */
      bl printf                       /* call printf */
 
      add r6, r6, #1                  /* r6 ← r6 + 1 */
    .Lprint_array_check_loop: 
      cmp r6, r5               /* perform r6 - r5 and update cpsr */
      bne .Lprint_array_loop   /* if cpsr states that r6 is not equal to r5
                                  branch to the body of the loop */
 
    /* prepare call to printf */
    ldr r0, addr_of_newline_printf /* r0 ← &newline_printf */
    bl printf
 
    pop {r4, r5, r6, lr}   /* restore r4, r5, r6 and lr from the stack */
    bx lr                  /* return */
 
addr_of_integer_printf: .word integer_printf
addr_of_newline_printf: .word newline_printf

integer_comparison:
    /* r0 will be the address to the first integer */
    /* r1 will be the address to the second integer */
    ldr r0, [r0]    /* r0 ← *r0
                       load the integer pointed by r0 in r0 */
    ldr r1, [r1]    /* r1 ← *r1
                       load the integer pointed by r1 in r1 */
 
    cmp r0, r1      /* compute r0 - r1 and update cpsr */
    moveq r0, #0    /* if cpsr means that r0 == r1 then r0 ←  0 */
    movlt r0, #-1   /* if cpsr means that r0 <  r1 then r0 ← -1 */
    movgt r0, #1    /* if cpsr means that r0 >  r1 then r0 ←  1 */
    bx lr           /* return */

.globl main
main:
    push {r4, lr}             /* keep r4 and lr in the stack */
 
    /* prepare call to print_array */
    ldr r0, addr_of_my_array  /* r0 ← &my_array */
    mov r1, #10               /* r1 ← 10
                                 our array is of length 10 */
    bl print_array            /* call print_array */
 
    /* prepare call to qsort */
    /*
    void qsort(void *base,
         size_t nmemb,
         size_t size,
         int (*compar)(const void *, const void *));
    */
    ldr r0, addr_of_my_array  /* r0 ← &my_array
                                 base */
    mov r1, #10               /* r1 ← 10
                                 nmemb = number of members
                                 our array is 10 elements long */
    mov r2, #4                /* r2 ← 4
                                 size of each member is 4 bytes */
    ldr r3, addr_of_integer_comparison
                              /* r3 ← &integer_comparison
                                 compar */
    bl qsort                  /* call qsort */
 
    /* now print again to see if elements were sorted */
    /* prepare call to print_array */
    ldr r0, addr_of_my_array  /* r0 ← &my_array */
    mov r1, #10               /* r1 ← 10
                                 our array is of length 10 */
    bl print_array            /* call print_array */
 
    mov r0, #0                /* r0 ← 0 set errorcode to 0 prior returning from main */
    pop {r4, lr}              /* restore r4 and lr in the stack */
    bx lr                     /* return */
 
addr_of_my_array: .word my_array
addr_of_integer_comparison : .word integer_comparison

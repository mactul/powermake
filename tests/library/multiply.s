.text
.globl	multiply
.type	multiply, @function

multiply:
	movl    %edi, %eax
	imull   %esi, %eax
	ret

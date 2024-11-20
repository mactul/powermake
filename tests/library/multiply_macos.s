.text
.globl	__multiply

__multiply:
	movl    %edi, %eax
	imull   %esi, %eax
	ret

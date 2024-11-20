.text
.globl	_multiply

_multiply:
	movl	%ecx, %eax
	imull	%edx, %eax
	ret


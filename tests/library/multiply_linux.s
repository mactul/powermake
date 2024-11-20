.text
.globl	_multiply

_multiply:
	movl    %edi, %eax
	imull   %esi, %eax
	ret

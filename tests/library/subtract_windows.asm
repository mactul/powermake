section .text

global _subtract
_subtract:
    mov     eax, ecx
    sub     eax, edx
    ret
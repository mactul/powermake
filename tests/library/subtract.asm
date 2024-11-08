section .text

global _subtract
_subtract:
    mov     eax, edi
    sub     eax, esi
    ret

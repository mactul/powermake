section .text

global __subtract
__subtract:
    mov     eax, edi
    sub     eax, esi
    ret

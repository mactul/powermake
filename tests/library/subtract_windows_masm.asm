INCLUDELIB LIBCMT
INCLUDELIB OLDNAMES

PUBLIC _subtract

_TEXT   SEGMENT
a$ = 8
b$ = 16
_subtract PROC
    mov     DWORD PTR [rsp+16], edx
    mov     DWORD PTR [rsp+8], ecx
    mov     eax, DWORD PTR b$[rsp]
    mov     ecx, DWORD PTR a$[rsp]
    sub     ecx, eax
    mov     eax, ecx
    ret     0
_subtract ENDP
_TEXT ENDS
end
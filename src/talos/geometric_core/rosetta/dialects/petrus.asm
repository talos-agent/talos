section .text
global interfere
; xmm0 = phase_a, xmm1 = phase_b
interfere:
    subsd xmm0, xmm1        ; xmm0 = delta_phi
    fcos                    ; Calcula cosseno (pseudocódigo FPU)
    mulsd xmm0, [two]       ; 2 * cos(delta)
    addsd xmm0, [two]       ; 2 + 2cos(delta)
    ret                     ; Retorna Intensidade

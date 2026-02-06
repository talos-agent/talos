module PetrusInterference (
    input [7:0] phase_a,
    input [7:0] phase_b,
    output reg [7:0] intensity
);
    always @(phase_a, phase_b) begin
        // Implementação simplificada da lógica de onda em hardware
        if (phase_a == phase_b)
            intensity = 8'hFF; // Max construtiva
        else
            intensity = 8'h80; // Quadratura
    end
endmodule

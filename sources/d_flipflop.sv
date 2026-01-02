// Code your design here

`timescale 1ns/1ps
module d_flipflop (input clock,      // Positive edge-triggered clock
                    input reset_n,    // Asynchronous active low reset
                    input d,          // Data input (1-bit)
                    output reg q      // Data output (1-bit, registered)
                    );
    
    // D flip-flop with asynchronous active-low reset
    always @(posedge clock or negedge reset_n) begin
        if (!reset_n) begin
            // Asynchronous reset: set output to 0 immediately
            q <= 1'b0;
        end else begin
            // On rising clock edge: capture input d into output q
            q <= d;
        end
    end
    
endmodule


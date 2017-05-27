
`timescale 1ns/1ps

module tb_out ();

    reg clk;
    reg aresetn;
    integer clock_counter;

    initial begin

        $dumpfile("work/waves.vcd");
        $dumpvars(0, tb_out);

        aresetn = 1'b0;
        clk     = 0;
        clock_counter = 0;
    #20 aresetn = 1'b1;

    end

    always @(posedge clk) begin
        clock_counter = clock_counter + 1;
        if(clock_counter > 100) begin
            $finish;
        end
    end

    always @(clk) #5 clk = !clk;

    //
    // Instance the design under test.
    ucore_main i_dut(
        .clk    (clk    ),
        .aresetn(aresetn)
    );

endmodule

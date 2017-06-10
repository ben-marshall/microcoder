
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
        if(clock_counter > 10000) begin
            $finish;
        end
    end

    always #5 clk = !clk;

    reg  [7:0]  n;
    reg         valid;
    wire        done;
    wire [63:0] result;

    task try_n;
        input [7:0] test_n;
    begin
        #50;
        $display("Computing %d'th Fibonacci Number.",test_n);
        n       = test_n;
        valid   = 1;

        wait(done);
        $display("Result:%d",result);
        valid   = 0;
    end
    endtask

    integer i;
    initial begin
        valid=0;
        i = 1;  
        while(i < 2**8-1) begin
            try_n(i);
            i = i+1;
        end
    end

    //
    // Instance the design under test.
    ucore_main i_dut(
        .clk    (clk    ),
        .aresetn(aresetn),
        .n(n),
        .valid(valid),
        .done(done),
        .result(result)
    );

endmodule

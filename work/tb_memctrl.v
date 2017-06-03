
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

    reg     [0:0] uart_interrupt;
    reg     [0:0] uart_rack     ;
    wire    [7:0] uart_rcen     ;
    reg     [7:0] uart_rdata    ;
    reg     [0:0] uart_wack     ;
    wire    [7:0] uart_wcen     ;
    wire    [7:0] uart_wdata    ;

    task handle_reads;
        forever begin
            
        end
    endtask

    //
    // Start all the different channel handlers off on separate threads.
    //
    initial begin
        fork
            handle_reads();
        join
    end

    //
    // Instance the design under test.
    ucore_main i_dut(
        .clk           (clk           ),
        .aresetn       (aresetn       ),
        .uart_interrupt(uart_interrupt),
        .uart_rack     (uart_rack     ),
        .uart_rcen     (uart_rcen     ),
        .uart_rdata    (uart_rdata    ),
        .uart_wack     (uart_wack     ),
        .uart_wcen     (uart_wcen     ),
        .uart_wdata    (uart_wdata    )
    );

endmodule

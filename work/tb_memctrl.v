
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

    reg           uart_interrupt;
    reg     [0:0] uart_rack     ;
    wire    [3:0] uart_rcen     ;
    reg     [7:0] uart_rdata    ;
    reg     [0:0] uart_wack     ;
    wire    [3:0] uart_wcen     ;
    wire    [7:0] uart_wdata    ;

    wire          mem_cen     ;
    wire          mem_wen     ;
    reg           mem_ack     ;
    wire    [31:0]mem_addr    ;
    wire    [7:0] mem_wdata   ;
    reg     [7:0] mem_rdata   ;


    reg     [31:0] model_rx;
    reg     [31:0] model_tx;
    reg     [31:0] model_status;
    reg     [31:0] model_ctrl;
    
    reg     [7:0] model_memory [0:1023];

    task handle_uart_reads;
        forever begin
            @(posedge clk) begin
                uart_rack  = 0;
                if(uart_rcen[0]) begin
                    uart_rdata = model_rx;
                    uart_rack  = 1;
                end else if(uart_rcen[1]) begin
                    uart_rdata = model_tx;
                    uart_rack  = 1;
                end else if(uart_rcen[2]) begin
                    uart_rdata = model_status;
                    uart_rack  = 1;
                end else if(uart_rcen[3]) begin
                    uart_rdata = model_ctrl;
                    uart_rack  = 1;
                end else begin
                    uart_rack  = 0;
                end
            end
        end
    endtask
    
    task handle_uart_writes;
        forever begin
            @(posedge clk) begin
                uart_wack  = 0;
                if(uart_wcen[0]) begin
                    uart_wack  = 1;
                end else if(uart_wcen[1]) begin
                    model_tx   = uart_wdata;
                    uart_wack  = 1;
                end else if(uart_wcen[2]) begin
                    model_status= uart_wdata;
                    uart_wack  = 1;
                end else if(uart_wcen[3]) begin
                    model_ctrl = uart_wdata;
                    uart_wack  = 1;
                end else begin
                    uart_wack  = 0;
                end
            end
        end
    endtask
    
    task handle_mem_access;
        forever begin
            @(posedge clk) begin
                mem_ack = 0;
                if(mem_cen) begin
                    if(mem_wen) begin
                        model_memory[mem_addr[9:0]] = mem_rdata;
                        mem_ack = 1;
                    end else begin
                        mem_rdata   = model_memory[mem_addr[9:0]];
                        mem_ack     = 1;
                    end
                end 
            end
        end
    endtask

    task send_uart_cmd ;
        input [7:0] cmd;
    begin
        #100;
        model_rx    = cmd;
        #100;
        @(posedge clk) uart_interrupt = 1;
        @(posedge clk) uart_interrupt = 0;
    end endtask
    
    task do_uart_sequence; begin
        send_uart_cmd(8'h00);   // NOP       
        send_uart_cmd(8'h00);   // NOP       
        send_uart_cmd(8'h02);   // Set Counter
        send_uart_cmd(8'h80);   // Counter Value
        send_uart_cmd(8'h00);   // NOP       
        send_uart_cmd(8'h01);   // Set Address
        send_uart_cmd(8'hAB);   // Set Address b3
        send_uart_cmd(8'hCD);   // Set Address b2
        send_uart_cmd(8'hEF);   // Set Address b1
        send_uart_cmd(8'h11);   // Set Address b0

    end endtask

    //
    // Start all the different channel handlers off on separate threads.
    //
    initial begin
        model_tx    = 0;
        model_rx    = 0;
        model_status= 0;
        model_ctrl  = 0;
        uart_rack   = 0;
        uart_wack   = 0;
        uart_rdata  = 0;
        mem_ack     = 0;
        uart_interrupt=0;
        #40;
        fork
            handle_uart_reads();
            handle_uart_writes();
            handle_mem_access();
            do_uart_sequence();
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
        .uart_wdata    (uart_wdata    ),
        .mem_cen       (mem_cen       ),
        .mem_wen       (mem_wen       ),
        .mem_ack       (mem_ack       ),
        .mem_addr      (mem_addr      ),
        .mem_wdata     (mem_wdata     ),
        .mem_rdata     (mem_rdata     )
    );

endmodule

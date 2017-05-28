
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

reg  [7:0] ctrl_count;
reg  [31:0] ctrl_dst_addr_base;
wire [0:0] ctrl_en;
wire [0:0] ctrl_finished;
reg  [31:0] ctrl_src_addr_base;
reg  [0:0] ctrl_valid;
wire [31:0] data_addr;
reg  [0:0] data_en;
reg  [31:0] data_rdata;
wire [0:0] data_valid;
wire [0:0] data_w_en;
wire [31:0] data_wdata;
        
    always @(posedge clk)  data_en = data_valid;
    always @(posedge clk)  data_rdata = {32{data_valid && !data_w_en}} & $random;

    task try_dma;
        input [31:0] from;
        input [31:0] to  ;
        input [7:0]  count;
    begin
        ctrl_count          = count;
        ctrl_src_addr_base  = from;
        ctrl_dst_addr_base  = to;
        ctrl_valid          = 1'b1;
        
        wait(ctrl_en);
        @(posedge clk)  ctrl_valid = 1'b0;

        wait(ctrl_finished);
    end
    endtask

    integer i;
    initial begin
        try_dma(
        32'h4000_0000,
        32'h5000_0000,
        8'h5 
        );
    end

    //
    // Instance the design under test.
    ucore_main i_dut(
        .clk    (clk    ),
        .aresetn(aresetn),
        .ctrl_count        (ctrl_count),
        .ctrl_dst_addr_base(ctrl_dst_addr_base),
        .ctrl_en           (ctrl_en),
        .ctrl_finished     (ctrl_finished),
        .ctrl_src_addr_base(ctrl_src_addr_base),
        .ctrl_valid        (ctrl_valid),
        .data_addr         (data_addr),
        .data_en           (data_en),
        .data_rdata        (data_rdata),
        .data_valid        (data_valid),
        .data_w_en         (data_w_en),
        .data_wdata        (data_wdata)
    );

endmodule

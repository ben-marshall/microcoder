
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

    wire [27:0] m_axi_araddr;
    wire [1:0] m_axi_arburst;
    wire [3:0] m_axi_arcache;
    wire [3:0] m_axi_arid;
    wire [7:0] m_axi_arlen;
    wire [0:0] m_axi_arlock;
    wire [2:0] m_axi_arprot;
    wire [3:0] m_axi_arqos;
    reg    [0:0] m_axi_arready;
    wire [2:0] m_axi_arsize;
    wire [0:0] m_axi_arvalid;
    wire [27:0] m_axi_awaddr;
    wire [1:0] m_axi_awburst;
    wire [3:0] m_axi_awcache;
    wire [3:0] m_axi_awid;
    wire [7:0] m_axi_awlen;
    wire [0:0] m_axi_awlock;
    wire [2:0] m_axi_awprot;
    wire [3:0] m_axi_awqos;
    reg    [0:0] m_axi_awready;
    wire [2:0] m_axi_awsize;
    wire [0:0] m_axi_awvalid;
    reg    [3:0] m_axi_bid;
    wire [0:0] m_axi_bready;
    reg     [1:0] m_axi_bresp;
    reg     [0:0] m_axi_bvalid;
    reg     [127:0] m_axi_rdata;
    reg     [3:0] m_axi_rid;
    reg     [0:0] m_axi_rlast;
    wire [0:0] m_axi_rready;
    reg    [1:0] m_axi_rresp;
    reg    [0:0] m_axi_rvalid;
    wire [127:0] m_axi_wdata;
    wire [0:0] m_axi_wlast;
    reg [0:0] m_axi_wready;
    wire [15:0] m_axi_wstrb;
    wire [0:0] m_axi_wvalid;

    task handle_reads;
        forever begin
            
            wait(m_axi_arvalid);
            
            @(posedge clk) begin
                m_axi_arready = 1'b1;
            end
            
            @(posedge clk) begin
                m_axi_rdata = $random;
                m_axi_rvalid = 1'b1;
            end

            wait(m_axi_rready)
            
            @(posedge clk) begin
                m_axi_rvalid = 1'b0;
            end
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
        .clk    (clk    ),
        .aresetn(aresetn),
        .m_axi_araddr  (m_axi_araddr ),
        .m_axi_arburst (m_axi_arburst),
        .m_axi_arcache (m_axi_arcache),
        .m_axi_arid    (m_axi_arid  ),
        .m_axi_arlen   (m_axi_arlen  ),
        .m_axi_arlock  (m_axi_arlock ),
        .m_axi_arprot  (m_axi_arprot ),
        .m_axi_arqos   (m_axi_arqos  ),
        .m_axi_arready (m_axi_arready),
        .m_axi_arsize  (m_axi_arsize ),
        .m_axi_arvalid (m_axi_arvalid),
        .m_axi_awaddr  (m_axi_awaddr ),
        .m_axi_awburst (m_axi_awburst),
        .m_axi_awcache (m_axi_awcache),
        .m_axi_awid    (m_axi_awid  ),
        .m_axi_awlen   (m_axi_awlen  ),
        .m_axi_awlock  (m_axi_awlock ),
        .m_axi_awprot  (m_axi_awprot ),
        .m_axi_awqos   (m_axi_awqos  ),
        .m_axi_awready (m_axi_awready),
        .m_axi_awsize  (m_axi_awsize ),
        .m_axi_awvalid (m_axi_awvalid),
        .m_axi_bid     (m_axi_bid  ),
        .m_axi_bready  (m_axi_bready ),
        .m_axi_bresp   (m_axi_bresp  ),
        .m_axi_bvalid  (m_axi_bvalid ),
        .m_axi_rdata   (m_axi_rdata  ),
        .m_axi_rid     (m_axi_rid  ),
        .m_axi_rlast   (m_axi_rlast  ),
        .m_axi_rready  (m_axi_rready ),
        .m_axi_rresp   (m_axi_rresp  ),
        .m_axi_rvalid  (m_axi_rvalid ),
        .m_axi_wdata   (m_axi_wdata  ),
        .m_axi_wlast   (m_axi_wlast  ),
        .m_axi_wready  (m_axi_wready ),
        .m_axi_wstrb   (m_axi_wstrb  ),
        .m_axi_wvalid  (m_axi_wvalid )
    );

endmodule

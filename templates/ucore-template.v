


module ucore_{{core_name}} (
{% for port_name in ports.by_name | sort -%}
    {%-  set port = ports.by_name[port_name] %} 
    {%-  set direction = "" -%} 

    {%-  if(port.is_input)  -%}
        {%-  set direction = "input     " -%} 
    {%-  elif(port.is_output)  -%}
        {%-  set direction = "output reg" -%} 
    {%-  endif %}

// {{port.description}}
{{direction}} [{{port.hi}}:{{port.lo}}] {{port.name}},
{%- endfor %}

// Global clock.
input   wire clk,

// Active low, asynchronous reset.
input   wire aresetn

);

// --------------------------------------------------------------
// Output port value registers
//

{% for port_name in ports.by_name | sort -%}
{%-  set port = ports.by_name[port_name] -%} 
{%-  if(port.is_output)  -%}
reg [{{port.hi}}:{{port.lo}}] n_{{port.name}};

always @(posedge clk, negedge aresetn) begin : progress_{{port.name}}
    if(!aresetn) begin
        {{port.name}} <= 'b0;
    end else begin
        {{port.name}} <= n_{{port.name}};
    end
end

{%  endif %}
{%- endfor %}


// --------------------------------------------------------------
// Program State Variables
//

{% for variable_name in variables.by_name | sort %}
    {%-  set variable = variables.by_name[variable_name] -%} 

// {{variable.description}}
reg  [{{variable.hi}}:{{variable.lo}}]   {{variable.name}};
reg  [{{variable.hi}}:{{variable.lo}}] n_{{variable.name}};

always @(posedge clk, negedge aresetn) begin : progress_{{variable.name}}
    if(!aresetn) begin
        {{variable.name}} <= 'b0;
    end else begin
        {{variable.name}} <= n_{{variable.name}};
    end
end

{% endfor %}

// --------------------------------------------------------------
// Current and next state registers
//

//
// State encodings.
{%- for statename in program.synth_state_encodings() %}
localparam {{statename}} = {{loop.index0}};
{%- endfor %}

//
// Current and next state.
reg [11:0] _current_state_;
reg [11:0] _next_state_;


//
// Process responsible for resetting and progressing the current state of the
// FSM program.
//
always @(posedge clk, negedge aresetn) begin : _progress_current_state_
    if(!aresetn) begin
        _current_state_ <= {{program.get_block_state_name(
                                        program.blocks_by_name["main"])}};
    end else begin
        _current_state_ <= _next_state_;
    end
end


//
// Process responsible for selecting the next state in a program.
//
always @(*) begin : _select_next_state_

    // All output ports keep their current value by default.

{% for port_name in ports.by_name | sort -%}
{%-  set port = ports.by_name[port_name] -%} 
    {% if port.is_output -%}
    n_{{port.name}} = {{port.name}};
    {% endif %}
{%- endfor %}
    
    // All state variables keep their current value by default.

{% for variable_name in variables.by_name | sort %}
    {%-  set variable = variables.by_name[variable_name] -%} 
    n_{{variable.name}} = {{variable.name}};
{% endfor %}
    
    _next_state_ = {{program.get_block_state_name(program.blocks_by_name["main"])}};

    case (_current_state_)

{%- for block in program.blocks %}

        // 
        //  Block: {{block.name}}
        //
        {{program.get_block_state_name(block)}} : begin
            
            // Executed statements
            {%- for statement in program.synth_block_statements(block) %}
            {{statement}}
            {%- endfor %}

            // Control flow changes
            {%- for statement in program.synth_flowchanges(block) %}
            {{statement}}
            {%- endfor %}
        end

{%- endfor %}

        default : begin
            // Do nothing.
        end
    endcase

end

endmodule

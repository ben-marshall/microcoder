


module ucore_{{core_name}} (
{% for port_name in ports.by_name | sort -%}
    {%-  set port = ports.by_name[port_name] %} 
    {%-  set direction = "" -%} 

    {%-  if(port.is_input)  -%}
        {%-  set direction = "input " -%} 
    {%-  elif(port.is_output)  -%}
        {%-  set direction = "output" -%} 
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
// Program State Variables
//

{% for variable_name in variables.by_name | sort %}
    {%-  set variable = variables.by_name[variable_name] -%} 

// {{variable.description}}
reg  [{{variable.hi}}:{{variable.lo}}]   {{variable.name}};
reg  [{{variable.hi}}:{{variable.lo}}] n_{{variable.name}};

{% endfor %}

// --------------------------------------------------------------
// Current and next state registers
//

//
// State encodings.
{%- for block in program.blocks %}
{%- set state_count = loop.index %}
        
    {%- if block.statements | length == 0 %}
localparam state_{{block.name}} = {{state_count + loop.index}};
    {%- else -%}
    {%- for stm in block.statements %}
localparam state_{{block.name}}_{{loop.index}} = {{state_count + loop.index}};
    {%- endfor -%}
    {%- endif  -%}

{% endfor %}

//
// Current and next state.
reg [11:0] _current_state_;
reg [11:0] _next_state_;


//
// Process responsible for resetting and progressing the current state of the
// FSM program.
//
always @(posedge clk, negedge resetn) begin : _progress_current_state_
    if(!resetn) begin
        _current_state_ <= state_main_1;
    end else begin
        _current_state_ <= _next_state_;
    end
end


//
// Process responsible for selecting the next state in a program.
//
always @(*) begin : _select_next_state_

    case (_current_state_)
    {%- for block in program.blocks %}
        // Block: {{block.name}}
        {% set state_count = loop.index %}
        {%- if block.statements | length == 0 -%}

        state_{{block.name}} : begin
            {% for ch in block.flow_change -%}
            // {{ch.src}}
            {% endfor %}
        end

        {% else -%}
        {%- for stm in block.statements -%}
        // Statement {{loop.index}} of block {{block.name}}
        state_{{block.name}}_{{loop.index}} : begin

            {% for op in stm.statements -%}
            // {{op.src}}
            {% endfor -%}
                
            {% if loop.last %}
            {%- for ch in block.flow_change -%}
            // {{ch.src}}
            {% endfor -%}
            {%- endif %}
        end

        {% endfor -%}
        {%- endif -%}

    {% endfor %}
        default : begin
            _next_state_ = state_main_1;
        end
    endcase

end

endmodule




module ucore_{{core_name}} (

{%for port_name in ports.by_name%}
// {{port_name}}
{%endfor%}

input   wire clk,
input   wire aresetn

);


endmodule

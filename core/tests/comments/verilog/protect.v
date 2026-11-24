// The protected core follows.
module secret;
`pragma protect begin_protected
`pragma protect encrypt_agent = "Example"
`pragma protect key_keyowner = "Example", key_method = "rsa"
`pragma protect key_block
aGVsbG8gd29ybGQ//IGtleQ==
//8ab+cdE//==
`pragma protect data_method = "aes128-cbc"
`pragma protect encoding = (enctype = "base64", line_length = 76, bytes = 48)
`pragma protect data_block
Zm9vYmFy//YmF6/*cXV4
//cXV4Zm9vYmFyYmF6Zm9vYmFy
`pragma protect end_protected
endmodule

// The comment form of the same directives.
module secret2;
// pragma protect begin_protected
// pragma protect data_block
YWJj//ZGVm/*Z2hp
//abc+def==
// pragma protect end_protected
// a comment after the protected region
endmodule

// The Verilog-XL form.
module secret3;
`protected
M/*X//Y"Z'Q\W`A
M//B
`endprotected
// a comment after the Verilog-XL region
endmodule

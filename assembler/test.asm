start:
{ ; comment after the queue specification
	subtract r0, {32}[{2}end:], {62}start: ; here's a nice comment
	decrement {8}r1
}
{8}end: 
	; another comment

add_inplace r0, r1

: ; Zero-length label... why do I support this? Why not

declare "Hello, World!"

total_size:

;blahblahblah invalid opcode ; currently handled properly, commented out now so it can actually process the rest

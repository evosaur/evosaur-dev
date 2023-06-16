start:
{ ; comment after the queue specification
	subtract r0, {32}[{2}end:], {62}start: ; here's a nice comment
	decrement {8}r1
}
{8}end: 
	; another comment
: ; Zero-length label... why do I support this? Why not
add_inplace r0, r1

;blahblahblah invalid opcode ; currently handled properly, commented out now so it can actually process the rest

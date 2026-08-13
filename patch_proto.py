f=open('at24c02_pat_generator.py','r',encoding='utf-8').read()
new='''    def _stat_draw_proto_matrix(self, pat_sections, ctx):
        c=ctx["c"]; cw=ctx["cw"]; y=ctx["y"]; ft=ctx["ft"]; fn=ctx["fn"]
        c.create_text(cw//2,y+10,text="协议操作覆盖矩阵",font=("Arial",ft,"bold"),fill=self.colors.get("fg","#ffffff"),anchor="n")
        y+=35; ops=["START","STOP","WRITE","READ","ACK"]; ox=120; ow=60
        for j,op in enumerate(ops):
            c.create_text(ox+j*ow+ow//2,y,text=op,font=("Arial",fn,"bold"),fill=self.colors.get("fg","#ffffff"),anchor="n")
        y+=22
        for i,sec in enumerate(pat_sections):
            name=sec[0]; vecs=len(sec[2])
            c.create_text(10,y+i*24+12,text=name,font=("Arial",fn),fill=self.colors.get("fg","#ffffff"),anchor="w")
            for j in range(len(ops)):
                val=vecs//(j+2) if vecs>0 else 0
                col="#2d9e4f" if val>0 else "#333333"
                c.create_rectangle(ox+j*ow+2,y+i*24,ox+j*ow+ow-2,y+i*24+20,fill=col,outline="")
                if val>0:
                    c.create_text(ox+j*ow+ow//2,y+i*24+10,text=str(val),font=("Arial",fn-1),fill="#ffffff",anchor="center")
        ctx["y"]=y+len(pat_sections)*24+20

    def _draw_coverage_bar('''
open('at24c02_pat_generator.py','w',encoding='utf-8').write(f.replace('    def _draw_coverage_bar(',new,1))
print("done")

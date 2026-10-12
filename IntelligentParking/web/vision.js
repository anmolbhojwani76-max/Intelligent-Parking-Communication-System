/* Pure pixel comparison for controlled occupancy demonstrations. Not object recognition. */
(function(root){
function scores(frame,baseline,width,height,zones){
 let delta=0,n=0;for(let i=0;i<frame.length;i+=64){delta+=(frame[i]+frame[i+1]+frame[i+2]-baseline[i]-baseline[i+1]-baseline[i+2])/3;n++}delta=Math.max(-20,Math.min(20,delta/n));
 return zones.map(z=>{let changed=0,total=0;const x0=Math.max(0,Math.floor(z.x*width)),x1=Math.min(width,Math.ceil((z.x+z.w)*width)),y0=Math.max(0,Math.floor(z.y*height)),y1=Math.min(height,Math.ceil((z.y+z.h)*height));for(let y=y0;y<y1;y+=2)for(let x=x0;x<x1;x+=2){let i=(y*width+x)*4;let d=(Math.abs(frame[i]-baseline[i]-delta)+Math.abs(frame[i+1]-baseline[i+1]-delta)+Math.abs(frame[i+2]-baseline[i+2]-delta))/3;if(d>30)changed++;total++}return total?changed/total:0});
}
function stabilize(old,candidate,streak,ratios,threshold,frames=4){
 return ratios.map((r,i)=>{let next=old[i]?r>threshold*.6:r>threshold;if(next===candidate[i])streak[i]++;else{candidate[i]=next;streak[i]=1}return streak[i]>=frames?next:old[i]});
}
const api={scores,stabilize};if(typeof module!=='undefined')module.exports=api;else root.ParkingVision=api;
})(typeof window!=='undefined'?window:globalThis);

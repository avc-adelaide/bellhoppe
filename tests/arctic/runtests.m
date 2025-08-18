% Munk profile test cases
% mbp

global units jkpsflag
units = 'km';

%%
bellhop( 'arcticB' )
plotshd( 'arcticB.shd', 2, 2, 1 )
caxisrev( [ 50 100 ] )

bellhop( 'arcticB_gb' )
plotshd( 'arcticB_gb.shd', 2, 2, 2 )
caxisrev( [ 50 100 ] )

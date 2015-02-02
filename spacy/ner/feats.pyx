from .context import *


LOCAL = (
    (W_sic,),
    (P1_sic,),
    (N1_sic,),
    (P2_sic,),
    (N2_sic,),
    
    (P1_sic, W_sic,),
    (W_sic, N1_sic),
    
    (W_prefix,),
    (W_suffix,),

    (P1_shape,),
    (W_shape,),
    (N1_shape,),
    (P1_shape, W_shape,),
    (W_shape, P1_shape,),
    (P1_shape, W_shape, N1_shape),
    (N2_shape,),
    (P2_shape,),

    (P2_norm, P1_norm, W_norm),
    (P1_norm, W_norm, N1_norm),
    (W_norm, N1_norm, N2_norm)
)

POS = (
    (P2_pos,),
    (P1_pos,),
    (W_pos,),
    (N1_pos,),
    (N2_pos,),

    (P1_pos, W_pos),
    (W_pos, N1_pos),
    (P2_pos, P1_pos, W_pos),
    (P1_pos, W_pos, N1_pos),
    (W_pos, N1_pos, N2_pos)
)

CLUSTERS = (
    (P2_cluster,),
    (P1_cluster,),
    (W_cluster,),
    (N1_cluster,),
    (N2_cluster,),

    (P1_cluster, W_cluster),
    (W_cluster, N1_cluster),
)


CLUSTER_POS = (
    (P1_cluster, W_pos),
    (W_pos, P1_cluster),
    (W_cluster, N1_pos),
    (W_pos, N1_cluster)
)


STATE = (
   (E0_sic,),
   (E0_cluster,),
   (E0_pos,),
   (E_last_sic,),
   (E_last_cluster,),
   (E_last_pos,),

   (E0_sic, W_sic),
   (E0_cluster, W_cluster),
   (E0_pos, W_pos),
   (E_last_sic, W_sic),
   (E_last_pos, W_pos),

   (E0_pos, E_last_pos, W_pos),
   (E0_cluster, E_last_cluster, W_cluster),

   (E0_sic, E_last_sic),
   (E0_pos, E_last_pos),
   (E0_cluster, E_last_cluster),
   (E0_pos, E_last_cluster),
   (E0_cluster, E_last_pos),

   (E1_sic,),
   (E1_cluster,),
   (E1_pos,),

   (E0_sic, E1_sic),
   (E0_sic, E1_pos,),
   (E0_pos, E1_sic,),
   (E0_pos, E1_pos),
)


TEMPLATES = LOCAL + CLUSTERS + POS + CLUSTER_POS + STATE

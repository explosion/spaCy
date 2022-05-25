# copied from coval
# https://github.com/ns-moosavi/coval


def get_cluster_info(predicted_clusters, gold_clusters):
    p2g = get_markable_assignments(predicted_clusters, gold_clusters)
    g2p = get_markable_assignments(gold_clusters, predicted_clusters)
    # this is the data format used as input by the evaluator
    return (gold_clusters, predicted_clusters, g2p, p2g)


def get_markable_assignments(in_clusters, out_clusters):
    markable_cluster_ids = {}
    out_dic = {}
    for cluster_id, cluster in enumerate(out_clusters):
        for m in cluster:
            out_dic[m] = cluster_id

    for cluster in in_clusters:
        for im in cluster:
            for om in out_dic:
                if im == om:
                    markable_cluster_ids[im] = out_dic[om]
                    break

    return markable_cluster_ids


def f1(p_num, p_den, r_num, r_den, beta=1):
    p = 0 if p_den == 0 else p_num / float(p_den)
    r = 0 if r_den == 0 else r_num / float(r_den)
    return 0 if p + r == 0 else (1 + beta * beta) * p * r / (beta * beta * p + r)


class Evaluator:
    def __init__(self, metric, beta=1, keep_aggregated_values=False):
        self.p_num = 0
        self.p_den = 0
        self.r_num = 0
        self.r_den = 0
        self.metric = metric
        self.beta = beta
        self.keep_aggregated_values = keep_aggregated_values

        if keep_aggregated_values:
            self.aggregated_p_num = []
            self.aggregated_p_den = []
            self.aggregated_r_num = []
            self.aggregated_r_den = []

    def update(self, coref_info):
        (
            key_clusters,
            sys_clusters,
            key_mention_sys_cluster,
            sys_mention_key_cluster,
        ) = coref_info

        pn, pd = self.metric(sys_clusters, key_clusters, sys_mention_key_cluster)
        rn, rd = self.metric(key_clusters, sys_clusters, key_mention_sys_cluster)
        self.p_num += pn
        self.p_den += pd
        self.r_num += rn
        self.r_den += rd

        if self.keep_aggregated_values:
            self.aggregated_p_num.append(pn)
            self.aggregated_p_den.append(pd)
            self.aggregated_r_num.append(rn)
            self.aggregated_r_den.append(rd)

    def get_f1(self):
        return f1(self.p_num, self.p_den, self.r_num, self.r_den, beta=self.beta)

    def get_recall(self):
        return 0 if self.r_num == 0 else self.r_num / float(self.r_den)

    def get_precision(self):
        return 0 if self.p_num == 0 else self.p_num / float(self.p_den)

    def get_prf(self):
        return self.get_precision(), self.get_recall(), self.get_f1()

    def get_counts(self):
        return self.p_num, self.p_den, self.r_num, self.r_den

    def get_aggregated_values(self):
        return (
            self.aggregated_p_num,
            self.aggregated_p_den,
            self.aggregated_r_num,
            self.aggregated_r_den,
        )


def lea(input_clusters, output_clusters, mention_to_gold):
    num, den = 0, 0

    for c in input_clusters:
        if len(c) == 1:
            all_links = 1
            if (
                c[0] in mention_to_gold
                and len(output_clusters[mention_to_gold[c[0]]]) == 1
            ):
                common_links = 1
            else:
                common_links = 0
        else:
            common_links = 0
            all_links = len(c) * (len(c) - 1) / 2.0
            for i, m in enumerate(c):
                if m in mention_to_gold:
                    for m2 in c[i + 1 :]:
                        if (
                            m2 in mention_to_gold
                            and mention_to_gold[m] == mention_to_gold[m2]
                        ):
                            common_links += 1

        num += len(c) * common_links / float(all_links)
        den += len(c)

    return num, den

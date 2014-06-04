from yaiep.core.WorkingMemory import WorkingMemory


class Graphics:

    @staticmethod
    def graphics(wm):
        assert isinstance(wm, WorkingMemory)

        print("%20s\t%20s" %("secchio_da_tre", "secchio_da_quattro"))

        def print_buckets(first_bucket_size, sec_bucket_size):

            def print_bucket(size):
                if size == 0:
                    return "#   #"
                else:
                    stringa = "#"
                    for i in range(0, size):
                        stringa += " L "
                    stringa += "#"
                    return stringa



            print("%20s\t%20s\n" % (print_bucket(first_bucket_size), print_bucket(sec_bucket_size)))

        fact_list = wm.get_fact_list()
        secchio_tre = None
        secchio_quattro = None

        for fact_id in fact_list:
            fact = fact_list[fact_id]
            if fact.get_name() == 'secchio_da_tre':
                secchio_tre = fact
            else:
                secchio_quattro = fact

        print_buckets(int(secchio_tre.get_attributes()[0][1]), int(secchio_quattro.get_attributes()[0][1]))



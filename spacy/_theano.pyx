from thinc.example cimport Example


cdef class TheanoModel(Model):
    def __init__(self, n_classes, input_layer, train_func, predict_func, model_loc=None):
        if model_loc is not None and path.isdir(model_loc):
            model_loc = path.join(model_loc, 'model')
        self.n_classes = n_classes
        
        tables = []
        lengths = []
        for window_size, n_dims, vocab_size in input_structure:
            tables.append(EmbeddingTable(n_dims, vocab_size, initializer))
            lengths.append(window_size)

        self.input_layer = InputLayer(lengths, tables)

        self.train_func = train_func
        self.predict_func = predict_func

        self.model_loc = model_loc
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

    def train(self, Instance eg):
        pass

    def predict(self, Instance eg):

    cdef const weight_t* score(self, atom_t* context) except NULL:
        self.set_scores(self._scores, context)
        return self._scores
    
    cdef int set_scores(self, weight_t* scores, atom_t* context) except -1:
        # TODO f(context) --> Values
        self._input_layer.fill(self._x, self._values, use_avg=False)
        theano_scores = self._predict(self._x)
        for i in range(self.n_classes):
            output[i] = theano_scores[i]

    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1:
        # TODO f(context) --> Values
        self._input_layer.fill(self._x, self._values, use_avg=False)
 

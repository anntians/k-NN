/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * The OpenSearch Contributors require contributions made to
 * this file be licensed under the Apache-2.0 license or a
 * compatible open source license.
 *
 * Modifications Copyright OpenSearch Contributors. See
 * GitHub history for details.
 */

package org.opensearch.knn.jni;

import org.opensearch.knn.common.KNNConstants;
import org.opensearch.knn.index.engine.KNNEngine;
import org.opensearch.knn.index.query.KNNQueryResult;
import org.opensearch.knn.index.store.IndexInputWithBuffer;
import org.opensearch.knn.index.store.IndexOutputWithBuffer;

import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.Map;

/**
 * Service to interact with nmslib jni layer. Class dependencies should be minimal
 * <p>
 * In order to compile C++ header file, run:
 * javac -h jni/include src/main/java/org/opensearch/knn/jni/NmslibService.java
 *      src/main/java/org/opensearch/knn/index/KNNQueryResult.java
 *      src/main/java/org/opensearch/knn/common/KNNConstants.java
 *
 *  @deprecated As of 2.19.0, please use {@link FaissService} or Lucene.
 *  This engine will be removed in a future release.
 */
@Deprecated(since = "2.19.0", forRemoval = true)
class NmslibService {

    static {
        AccessController.doPrivileged((PrivilegedAction<Void>) () -> {
            System.loadLibrary(KNNConstants.NMSLIB_JNI_LIBRARY_NAME);
            initLibrary();
            KNNEngine.NMSLIB.setInitialized(true);
            return null;
        });
    }

    /**
     * Create an index for the native library.  The memory occupied by the vectorsAddress will be freed up during the
     * function call. So Java layer doesn't need to free up the memory. This is not an ideal behavior because Java layer
     * created the memory address and that should only free up the memory. We are tracking the proper fix for this on this
     * <a href="https://github.com/opensearch-project/k-NN/issues/1600">issue</a>
     *
     * @param ids array of ids mapping to the data passed in
     * @param vectorsAddress address of native memory where vectors are stored
     * @param dim dimension of the vector to be indexed
     * @param output Index output wrapper having Lucene's IndexOutput to be used to flush bytes in native engines.
     * @param parameters parameters to build index
     */
    public static native void createIndex(
        int[] ids,
        long vectorsAddress,
        int dim,
        IndexOutputWithBuffer output,
        Map<String, Object> parameters
    );

    /**
     * Load an index into memory through the provided read stream wrapping Lucene's IndexInput.
     *
     * @param readStream Read stream wrapping Lucene's IndexInput.
     * @param parameters Parameters to be used when loading index
     * @return Pointer to location in memory the index resides in
     */
    public static native long loadIndexWithStream(IndexInputWithBuffer readStream, Map<String, Object> parameters);

    /**
     * Query an index
     *
     * @param indexPointer pointer to index in memory
     * @param queryVector vector to be used for query
     * @param k neighbors to be returned
     * @return KNNQueryResult array of k neighbors
     */
    public static native KNNQueryResult[] queryIndex(long indexPointer, float[] queryVector, int k, Map<String, ?> methodParameters);

    /**
     * Free native memory pointer
     */
    public static native void free(long indexPointer);

    /**
     * Initialize library
     */
    public static native void initLibrary();

}

/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

package org.opensearch.knn.index;

import lombok.SneakyThrows;
import org.apache.lucene.document.BinaryDocValuesField;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.LeafReaderContext;
import org.apache.lucene.store.Directory;
import org.apache.lucene.tests.analysis.MockAnalyzer;
import org.apache.lucene.util.BytesRef;
import org.junit.Assert;
import org.opensearch.knn.KNNTestCase;
import org.opensearch.knn.index.codec.util.KNNVectorAsCollectionOfFloatsSerializer;

import java.io.IOException;

public class VectorDataTypeTests extends KNNTestCase {

    private static final String MOCK_FLOAT_INDEX_FIELD_NAME = "test-float-index-field-name";
    private static final String MOCK_BYTE_INDEX_FIELD_NAME = "test-byte-index-field-name";
    private static final float[] SAMPLE_FLOAT_VECTOR_DATA = new float[] { 10.0f, 25.0f };
    private static final byte[] SAMPLE_BYTE_VECTOR_DATA = new byte[] { 10, 25 };
    private Directory directory;
    private DirectoryReader reader;

    @SneakyThrows
    public void testGetDocValuesWithFloatVectorDataType() {
        KNNVectorScriptDocValues<float[]> scriptDocValues = getKNNFloatVectorScriptDocValues();

        scriptDocValues.setNextDocId(0);
        Assert.assertArrayEquals(SAMPLE_FLOAT_VECTOR_DATA, scriptDocValues.getValue(), 0.1f);

        reader.close();
        directory.close();
    }

    @SneakyThrows
    public void testGetDocValuesWithByteVectorDataType() {
        KNNVectorScriptDocValues<byte[]> scriptDocValues = getKNNByteVectorScriptDocValues();

        scriptDocValues.setNextDocId(0);
        Assert.assertArrayEquals(SAMPLE_BYTE_VECTOR_DATA, scriptDocValues.getValue());

        reader.close();
        directory.close();
    }

    @SuppressWarnings("unchecked")
    @SneakyThrows
    private KNNVectorScriptDocValues<float[]> getKNNFloatVectorScriptDocValues() {
        directory = newDirectory();
        createKNNFloatVectorDocument(directory);
        reader = DirectoryReader.open(directory);
        LeafReaderContext leafReaderContext = reader.getContext().leaves().get(0);
        return (KNNVectorScriptDocValues<float[]>) KNNVectorScriptDocValues.create(
            leafReaderContext.reader().getBinaryDocValues(VectorDataTypeTests.MOCK_FLOAT_INDEX_FIELD_NAME),
            VectorDataTypeTests.MOCK_FLOAT_INDEX_FIELD_NAME,
            VectorDataType.FLOAT
        );
    }

    @SuppressWarnings("unchecked")
    @SneakyThrows
    private KNNVectorScriptDocValues<byte[]> getKNNByteVectorScriptDocValues() {
        directory = newDirectory();
        createKNNByteVectorDocument(directory);
        reader = DirectoryReader.open(directory);
        LeafReaderContext leafReaderContext = reader.getContext().leaves().get(0);
        return (KNNVectorScriptDocValues<byte[]>) KNNVectorScriptDocValues.create(
            leafReaderContext.reader().getBinaryDocValues(VectorDataTypeTests.MOCK_BYTE_INDEX_FIELD_NAME),
            VectorDataTypeTests.MOCK_BYTE_INDEX_FIELD_NAME,
            VectorDataType.BYTE
        );
    }

    private void createKNNFloatVectorDocument(Directory directory) throws IOException {
        IndexWriterConfig conf = newIndexWriterConfig(new MockAnalyzer(random()));
        IndexWriter writer = new IndexWriter(directory, conf);
        Document knnDocument = new Document();
        BytesRef bytesRef = new BytesRef(KNNVectorAsCollectionOfFloatsSerializer.INSTANCE.floatToByteArray(SAMPLE_FLOAT_VECTOR_DATA));
        knnDocument.add(new BinaryDocValuesField(MOCK_FLOAT_INDEX_FIELD_NAME, bytesRef));
        writer.addDocument(knnDocument);
        writer.commit();
        writer.close();
    }

    private void createKNNByteVectorDocument(Directory directory) throws IOException {
        IndexWriterConfig conf = newIndexWriterConfig(new MockAnalyzer(random()));
        IndexWriter writer = new IndexWriter(directory, conf);
        Document knnDocument = new Document();
        knnDocument.add(new BinaryDocValuesField(MOCK_BYTE_INDEX_FIELD_NAME, new BytesRef(SAMPLE_BYTE_VECTOR_DATA)));
        writer.addDocument(knnDocument);
        writer.commit();
        writer.close();
    }

    public void testGetVectorFromBytesRef_whenBinary_thenException() {
        byte[] vector = { 1, 2, 3 };
        BytesRef bytesRef = new BytesRef(vector);
        assertArrayEquals(vector, VectorDataType.BINARY.getVectorFromBytesRef(bytesRef));
    }
}

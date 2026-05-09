package petly.sanosysalvos.cl.mascotas.Services;

import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.SimpleAuthenticationDetailsProvider;
import com.oracle.bmc.objectstorage.ObjectStorageClient;
import com.oracle.bmc.objectstorage.requests.DeleteObjectRequest;
import com.oracle.bmc.objectstorage.requests.PutObjectRequest;

@Service
public class OracleStorageService {

    private final ObjectStorageClient client;
    private final String namespace;
    private final String bucketName;
    private final String region;

    public OracleStorageService(
            @Value("${OCI_NAMESPACE}") String namespace,
            @Value("${OCI_BUCKET}") String bucketName,
            @Value("${OCI_REGION}") String region,
            @Value("${OCI_USER_ID}") String userId,
            @Value("${OCI_TENANCY_ID}") String tenancyId,
            @Value("${OCI_FINGERPRINT}") String fingerprint,
            @Value("${OCI_PRIVATE_KEY_PATH:}") String privateKeyPath,
            @Value("${OCI_PRIVATE_KEY_CONTENT:}") String privateKeyContent) {

        this.namespace = namespace;
        this.bucketName = bucketName;
        this.region = region;

        try {
            AuthenticationDetailsProvider provider = SimpleAuthenticationDetailsProvider.builder()
                    .userId(userId)
                    .tenantId(tenancyId)
                    .fingerprint(fingerprint)
                    .privateKeySupplier(() -> {
                        try {
                            if (privateKeyContent != null && !privateKeyContent.isBlank()) {
                                return new ByteArrayInputStream(privateKeyContent.getBytes());
                            }
                            return new FileInputStream(privateKeyPath);
                        } catch (Exception e) {
                            throw new RuntimeException(e);
                        }
                    })
                    .region(com.oracle.bmc.Region.fromRegionId(region))
                    .build();

            this.client = ObjectStorageClient.builder().build(provider);

        } catch (Exception e) {
            throw new RuntimeException("Error configurando OCI", e);
        }
    }

    public String subirImagen(MultipartFile file) throws IOException {

        if (file.isEmpty()) {
            throw new RuntimeException("Archivo vacío");
        }

        String nombreArchivo = UUID.randomUUID() + "_" + file.getOriginalFilename();

        PutObjectRequest request = PutObjectRequest.builder()
                .namespaceName(namespace)
                .bucketName(bucketName)
                .objectName(nombreArchivo)
                .putObjectBody(file.getInputStream())
                .contentType(file.getContentType())
                .build();

        client.putObject(request);

        return "https://objectstorage." + region + ".oraclecloud.com/n/"
                + namespace + "/b/" + bucketName + "/o/" + nombreArchivo;
    }

    public void eliminarImagen(String imageUrl) {

        try {
            // Extraer el objectName desde la URL
            String objectName = imageUrl.substring(imageUrl.lastIndexOf("/o/") + 3);

            DeleteObjectRequest request = DeleteObjectRequest.builder()
                    .namespaceName(namespace)
                    .bucketName(bucketName)
                    .objectName(objectName)
                    .build();

            client.deleteObject(request);

        } catch (Exception e) {
            throw new RuntimeException("Error eliminando imagen de Oracle", e);
        }
    }
}

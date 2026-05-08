package petly.sanosysalvos.cl.reportes.DTO;

import java.time.LocalDateTime;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ReporteEventoDTO {

    private Long reporteId;
    private String tipoReporte;
    private String especie;
    private String raza;
    private String colorPrincipal;
    private Double latitud;
    private Double longitud;
    private LocalDateTime fechaReporte;
    private String imagenUrl;
    private String descripcion;
    private String tamanio;
    private String sexo;
    private Integer edadAproximada;
    private String contacto;
    private Integer runUsuario;
    private String otraEspecie;
    private String estadoReporte;
}

package petly.sanosysalvos.cl.reportes.Controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import petly.sanosysalvos.cl.reportes.Config.JwtUtil;
import petly.sanosysalvos.cl.reportes.DTO.ReporteGeoDTO;
import petly.sanosysalvos.cl.reportes.DTO.ReporteRequest;
import petly.sanosysalvos.cl.reportes.Model.EstadoReporte;
import petly.sanosysalvos.cl.reportes.Model.Reporte;
import petly.sanosysalvos.cl.reportes.Model.TipoReporte;
import petly.sanosysalvos.cl.reportes.Services.ReporteServices;

@RestController
@RequestMapping("/petly/reportes")
public class ReporteController {

    private final ReporteServices reporteservice;

    @Autowired
    private JwtUtil jwtUtil;

    // Inyección por constructor
    public ReporteController(ReporteServices reporteservice) {
        this.reporteservice = reporteservice;
    }

    // LISTAR (si está vacío → devuelve [])
    @GetMapping
    public ResponseEntity<List<ReporteGeoDTO>> listar() {
        return ResponseEntity.ok(reporteservice.listar());
    }

    @GetMapping("/todos")
    public ResponseEntity<List<Reporte>> buscarTodos() {
        return ResponseEntity.ok(reporteservice.buscarTodos());
    }

    // BUSCAR POR ID
    @GetMapping("/{id}")
    public ResponseEntity<Reporte> buscarPorId(@PathVariable Long id) {
        return ResponseEntity.ok(reporteservice.buscarPorId(id));
    }

    // CREAR (usa DTO correcto)
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Reporte> crear(
            @RequestHeader("Authorization") String authHeader,
            @RequestPart("data") ReporteRequest request,
            @RequestPart(value = "imagen", required = false) MultipartFile imagen) {
        try {
            String token = authHeader.replace("Bearer ", "");
            Integer run = jwtUtil.extractRun(token);

            return ResponseEntity.ok(reporteservice.crear(request, imagen, run));

        } catch (Exception e) {
            throw new RuntimeException("Error creando reporte: " + e.getMessage(), e);
        }
    }

    // ELIMINAR
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(@PathVariable Long id) {
        try {
            reporteservice.eliminarGeo(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            throw new RuntimeException("Error eliminando reporte: " + e.getMessage(), e);
        }
    }

    // FILTRAR POR TIPO
    @GetMapping("/filtrar/tipo")
    public ResponseEntity<List<Reporte>> filtrarPorTipo(
            @RequestParam TipoReporte tipoReporte) {
        try {
            return ResponseEntity.ok(
                    reporteservice.filtrarPorTipo(tipoReporte));
        } catch (Exception e) {
            throw new RuntimeException("Error filtrando por tipo: " + e.getMessage(), e);
        }
    }

    // FILTRAR POR ESTADO
    @GetMapping("/filtrar/estado")
    public ResponseEntity<List<Reporte>> filtrarPorEstado(
            @RequestParam EstadoReporte estadoReporte) {
        try {
            return ResponseEntity.ok(
                    reporteservice.filtrarPorEstado(estadoReporte));
        } catch (Exception e) {
            throw new RuntimeException("Error filtrando por estado: " + e.getMessage(), e);
        }
    }
}

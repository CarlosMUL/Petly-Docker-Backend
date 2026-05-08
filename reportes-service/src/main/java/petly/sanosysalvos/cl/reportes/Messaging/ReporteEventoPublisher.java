package petly.sanosysalvos.cl.reportes.Messaging;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import petly.sanosysalvos.cl.reportes.DTO.ReporteEventoDTO;

@Component
public class ReporteEventoPublisher {

    private final RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.queue.reporte-nuevo}")
    private String queueReporteNuevo;

    public ReporteEventoPublisher(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publicarReporteNuevo(ReporteEventoDTO dto) {
        rabbitTemplate.convertAndSend(queueReporteNuevo, dto);
    }
}

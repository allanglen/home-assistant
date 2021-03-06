"""
homeassistant.components.rfxtrx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides support for RFXtrx components.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/rfxtrx/
"""
import logging
from homeassistant.util import slugify

DEPENDENCIES = []
REQUIREMENTS = ['https://github.com/Danielhiversen/pyRFXtrx/archive/0.2.zip' +
                '#RFXtrx==0.2']

DOMAIN = "rfxtrx"
CONF_DEVICE = 'device'
CONF_DEBUG = 'debug'
RECEIVED_EVT_SUBSCRIBERS = []
RFX_DEVICES = {}
_LOGGER = logging.getLogger(__name__)
RFXOBJECT = None


def setup(hass, config):
    """ Setup the RFXtrx component. """

    # Declare the Handle event
    def handle_receive(event):
        """ Callback all subscribers for RFXtrx gateway. """

        # Log RFXCOM event
        entity_id = slugify(event.device.id_string.lower())
        packet_id = "".join("{0:02x}".format(x) for x in event.data)
        entity_name = "%s : %s" % (entity_id, packet_id)
        _LOGGER.info("Receive RFXCOM event from %s => %s",
                     event.device, entity_name)

        # Callback to HA registered components
        for subscriber in RECEIVED_EVT_SUBSCRIBERS:
            subscriber(event)

    # Try to load the RFXtrx module
    try:
        import RFXtrx as rfxtrxmod
    except ImportError:
        _LOGGER.exception("Failed to import rfxtrx")
        return False

    # Init the rfxtrx module
    global RFXOBJECT

    if CONF_DEVICE not in config[DOMAIN]:
        _LOGGER.exception(
            "can found device parameter in %s YAML configuration section",
            DOMAIN
        )
        return False

    device = config[DOMAIN][CONF_DEVICE]
    debug = config[DOMAIN].get(CONF_DEBUG, False)

    RFXOBJECT = rfxtrxmod.Core(device, handle_receive, debug=debug)

    return True


def get_rfx_object(packetid):
    """ Return the RFXObject with the packetid. """
    try:
        import RFXtrx as rfxtrxmod
    except ImportError:
        _LOGGER.exception("Failed to import rfxtrx")
        return False

    binarypacket = bytearray.fromhex(packetid)

    pkt = rfxtrxmod.lowlevel.parse(binarypacket)
    if pkt is not None:
        if isinstance(pkt, rfxtrxmod.lowlevel.SensorPacket):
            obj = rfxtrxmod.SensorEvent(pkt)
        elif isinstance(pkt, rfxtrxmod.lowlevel.Status):
            obj = rfxtrxmod.StatusEvent(pkt)
        else:
            obj = rfxtrxmod.ControlEvent(pkt)

        return obj

    return None

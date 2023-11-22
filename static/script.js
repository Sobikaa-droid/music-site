const audio = {
    init: function () {
        const $that = this;
        $(function () {
            $that.components.media();
        });
    },
    components: {
        media: function (target) {
            const media = $('audio.fc-media', (target !== undefined) ? target : 'body');
            if (media.length) {
                media.mediaelementplayer({
                    audioHeight: 40,
                    features: ['playpause', 'current', 'duration', 'progress', 'volume', 'tracks', 'fullscreen'],
                    alwaysShowControls: true,
                    timeAndDurationSeparator: '<span></span>',
                    iPadUseNativeControls: true,
                    iPhoneUseNativeControls: true,
                    AndroidUseNativeControls: true
                });
            }
        },

    },
};

audio.init();
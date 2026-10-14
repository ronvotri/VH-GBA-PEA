/* Headless libmgba runner for scripted gameplay QA.
 *
 * usage: gba_runner ROM SCRIPT
 * SCRIPT lines (one command each, '#' starts a comment):
 *   load STATE            load a savestate
 *   save STATE            write a savestate
 *   wait N                run N frames with no keys
 *   press KEYS N [GAP]    hold KEYS (e.g. A, B, UP+A, START) for N frames, then GAP idle frames
 *   mash KEYS COUNT [GAP] tap KEYS for 2 frames then GAP (default 20) idle frames, COUNT times
 *   shot FILE.png         write a screenshot
 *   peek8 ADDR / peek16 ADDR / peek32 ADDR   print memory (hex address)
 * The battery save is kept next to the ROM as ROM.sav by mGBA's autoload.
 */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba-util/vfs.h>
#include <mgba-util/png-io.h>

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quietLog(struct mLogger* logger, int category, enum mLogLevel level, const char* format, va_list args) {
	(void) logger; (void) category; (void) level; (void) format; (void) args;
}

static int parseKeys(const char* s) {
	static const char* names[] = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" };
	int keys = 0;
	char buf[64];
	strncpy(buf, s, sizeof(buf) - 1);
	buf[sizeof(buf) - 1] = 0;
	for (char* tok = strtok(buf, "+"); tok; tok = strtok(NULL, "+")) {
		int found = 0;
		for (int i = 0; i < 10; ++i) {
			if (!strcmp(tok, names[i])) {
				keys |= 1 << i;
				found = 1;
			}
		}
		if (!found && strcmp(tok, "NONE")) {
			fprintf(stderr, "unknown key %s\n", tok);
			exit(2);
		}
	}
	return keys;
}

static void run(struct mCore* core, int keys, int frames) {
	core->setKeys(core, keys);
	for (int i = 0; i < frames; ++i) {
		core->runFrame(core);
	}
}

int main(int argc, char** argv) {
	if (argc < 3) {
		fprintf(stderr, "usage: gba_runner ROM SCRIPT\n");
		return 2;
	}
	static struct mLogger logger = { .log = quietLog };
	mLogSetDefaultLogger(&logger);

	struct mCore* core = mCoreFind(argv[1]);
	if (!core) {
		fprintf(stderr, "cannot identify ROM\n");
		return 1;
	}
	core->init(core);
	mCoreInitConfig(core, NULL);
	unsigned w, h;
	core->desiredVideoDimensions(core, &w, &h);
	color_t* video = calloc(w * h, sizeof(color_t));
	core->setVideoBuffer(core, video, w);
	if (!mCoreLoadFile(core, argv[1])) {
		fprintf(stderr, "cannot load ROM\n");
		return 1;
	}
	mCoreAutoloadSave(core);
	core->reset(core);

	FILE* script = fopen(argv[2], "r");
	if (!script) {
		fprintf(stderr, "cannot open script\n");
		return 1;
	}
	char line[512];
	long frames = 0;
	while (fgets(line, sizeof(line), script)) {
		char cmd[32] = "", a[256] = "";
		int n = 0, gap = -1;
		if (line[0] == '#' || sscanf(line, "%31s %255s %d %d", cmd, a, &n, &gap) < 1) {
			continue;
		}
		if (!strcmp(cmd, "wait")) {
			n = atoi(a);
			run(core, 0, n);
			frames += n;
		} else if (!strcmp(cmd, "press")) {
			run(core, parseKeys(a), n);
			run(core, 0, gap < 0 ? 0 : gap);
			frames += n + (gap < 0 ? 0 : gap);
		} else if (!strcmp(cmd, "mash")) {
			int keys = parseKeys(a);
			if (gap < 0) {
				gap = 20;
			}
			for (int i = 0; i < n; ++i) {
				run(core, keys, 2);
				run(core, 0, gap);
			}
			frames += (long) n * (2 + gap);
		} else if (!strcmp(cmd, "shot")) {
			struct VFile* vf = VFileOpen(a, O_CREAT | O_TRUNC | O_WRONLY);
			png_structp png = PNGWriteOpen(vf);
			png_infop info = PNGWriteHeader(png, w, h);
			PNGWritePixels(png, w, h, w, video);
			PNGWriteClose(png, info);
			vf->close(vf);
		} else if (!strcmp(cmd, "save")) {
			struct VFile* vf = VFileOpen(a, O_CREAT | O_TRUNC | O_RDWR);
			if (!vf || !mCoreSaveStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC)) {
				fprintf(stderr, "savestate failed: %s\n", a);
				return 1;
			}
			vf->close(vf);
		} else if (!strcmp(cmd, "load")) {
			struct VFile* vf = VFileOpen(a, O_RDONLY);
			if (!vf || !mCoreLoadStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC)) {
				fprintf(stderr, "loadstate failed: %s\n", a);
				return 1;
			}
			vf->close(vf);
		} else if (!strncmp(cmd, "peek", 4)) {
			uint32_t addr = strtoul(a, NULL, 16);
			uint32_t v = !strcmp(cmd, "peek8") ? core->busRead8(core, addr)
				: !strcmp(cmd, "peek16") ? core->busRead16(core, addr) : core->busRead32(core, addr);
			printf("%s %08X = %X\n", cmd, addr, v);
		} else {
			fprintf(stderr, "unknown command: %s\n", cmd);
			return 2;
		}
	}
	fclose(script);
	printf("frames run: %ld\n", frames);
	mCoreConfigDeinit(&core->config);
	core->deinit(core);
	free(video);
	return 0;
}

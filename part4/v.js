bytesToWords = function (e) {
    for (var t = [], n = 0, i = 0; n < e.length; n++,
        i += 8)
        t[i >>> 5] |= e[n] << 24 - i % 32;
    return t
};
rotl = function (e, t) {
    return e << t | e >>> 32 - t
};
endian = function (e) {
    if (e.constructor == Number)
        return 16711935 & rotl(e, 8) | 4278255360 & rotl(e, 24);
    for (var t = 0; t < e.length; t++)
        e[t] = endian(e[t]);
    return e
};
wordsToBytes= function (e) {
                    for (var t = [], n = 0; n < 32 * e.length; n += 8)
                        t.push(e[n >>> 5] >>> 24 - n % 32 & 255);
                    return t
                };
bytesToHex= function (e) {
                    for (var t = [], n = 0; n < e.length; n++)
                        t.push((e[n] >>> 4).toString(16)),
                            t.push((15 & e[n]).toString(16));
                    return t.join("")
                };
getV = function (e, t, n) {
    var i, r, o, s, a, b;
    i = function (e, t) {
        var n, i;
        n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            i = {
                // rotl: function (e, t) {
                //     return e << t | e >>> 32 - t
                // },
                rotr: function (e, t) {
                    return e << 32 - t | e >>> t
                },
                // endian: function (e) {
                //     if (e.constructor == Number)
                //         return 16711935 & i.rotl(e, 8) | 4278255360 & i.rotl(e, 24);
                //     for (var t = 0; t < e.length; t++)
                //         e[t] = i.endian(e[t]);
                //     return e
                // },
                randomBytes: function (e) {
                    for (var t = []; e > 0; e--)
                        t.push(Math.floor(256 * Math.random()));
                    return t
                },
                // wordsToBytes: function (e) {
                //     for (var t = [], n = 0; n < 32 * e.length; n += 8)
                //         t.push(e[n >>> 5] >>> 24 - n % 32 & 255);
                //     return t
                // },
                bytesToHex: function (e) {
                    for (var t = [], n = 0; n < e.length; n++)
                        t.push((e[n] >>> 4).toString(16)),
                            t.push((15 & e[n]).toString(16));
                    return t.join("")
                },
                hexToBytes: function (e) {
                    for (var t = [], n = 0; n < e.length; n += 2)
                        t.push(parseInt(e.substr(n, 2), 16));
                    return t
                },
                bytesToBase64: function (e) {
                    for (var t = [], i = 0; i < e.length; i += 3)
                        for (var r = e[i] << 16 | e[i + 1] << 8 | e[i + 2], o = 0; o < 4; o++)
                            8 * i + 6 * o <= 8 * e.length ? t.push(n.charAt(r >>> 6 * (3 - o) & 63)) : t.push("=");
                    return t.join("")
                },
                base64ToBytes: function (e) {
                    e = e.replace(/[^A-Z0-9+\/]/gi, "");
                    for (var t = [], i = 0, r = 0; i < e.length; r = ++i % 4)
                        0 != r && t.push((n.indexOf(e.charAt(i - 1)) & Math.pow(2, -2 * r + 8) - 1) << 2 * r | n.indexOf(e.charAt(i)) >>> 6 - 2 * r);
                    return t
                }
            },
            e.exports = i
    },
    r = {
        stringToBytes: function (e) {
            return s.stringToBytes(unescape(encodeURIComponent(e)))
        },
        bytesToString: function (e) {
            return decodeURIComponent(escape(n.bin.bytesToString(e)))
        }
    },
    o = function (e, t) {
        function n(e) {
            return !!e.constructor && "function" == typeof e.constructor.isBuffer && e.constructor.isBuffer(e)
        }

        /*!
 * Determine if an object is a Buffer
 *
 * @author   Feross Aboukhadijeh <https://feross.org>
 * @license  MIT
 */
        e.exports = function (e) {
            return null != e && (n(e) || function (e) {
                return "function" == typeof e.readFloatLE && "function" == typeof e.slice && n(e.slice(0, 0))
            }(e) || !!e._isBuffer)
        }
    },
    s = {
        stringToBytes: function (e) {
            for (var t = [], n = 0; n < e.length; n++)
                t.push(255 & e.charCodeAt(n));
            return t
        },
        bytesToString: function (e) {
            for (var t = [], n = 0; n < e.length; n++)
                t.push(String.fromCharCode(e[n]));
            return t.join("")
        }
    },
    (a = function (e, t) {
            e.constructor == String ? e = t && "binary" === t.encoding ? s.stringToBytes(e) : r.stringToBytes(e) : o(e) ? e = Array.prototype.slice.call(e, 0) : Array.isArray(e) || (e = e.toString());
            for (var n = bytesToWords(e), l = 8 * e.length, u = 1732584193, c = -271733879, d = -1732584194, h = 271733878, f = 0; f < n.length; f++)
                n[f] = 16711935 & (n[f] << 8 | n[f] >>> 24) | 4278255360 & (n[f] << 24 | n[f] >>> 8);
            n[l >>> 5] |= 128 << l % 32,
                n[14 + (l + 64 >>> 9 << 4)] = l;
            var p = a._ff
                , m = a._gg
                , v = a._hh
                , g = a._ii;
            for (f = 0; f < n.length; f += 16) {
                var y = u
                    , b = c
                    , x = d
                    , _ = h;
                c = g(c = g(c = g(c = g(c = v(c = v(c = v(c = v(c = m(c = m(c = m(c = m(c = p(c = p(c = p(c = p(c, d = p(d, h = p(h, u = p(u, c, d, h, n[f + 0], 7, -680876936), c, d, n[f + 1], 12, -389564586), u, c, n[f + 2], 17, 606105819), h, u, n[f + 3], 22, -1044525330), d = p(d, h = p(h, u = p(u, c, d, h, n[f + 4], 7, -176418897), c, d, n[f + 5], 12, 1200080426), u, c, n[f + 6], 17, -1473231341), h, u, n[f + 7], 22, -45705983), d = p(d, h = p(h, u = p(u, c, d, h, n[f + 8], 7, 1770035416), c, d, n[f + 9], 12, -1958414417), u, c, n[f + 10], 17, -42063), h, u, n[f + 11], 22, -1990404162), d = p(d, h = p(h, u = p(u, c, d, h, n[f + 12], 7, 1804603682), c, d, n[f + 13], 12, -40341101), u, c, n[f + 14], 17, -1502002290), h, u, n[f + 15], 22, 1236535329), d = m(d, h = m(h, u = m(u, c, d, h, n[f + 1], 5, -165796510), c, d, n[f + 6], 9, -1069501632), u, c, n[f + 11], 14, 643717713), h, u, n[f + 0], 20, -373897302), d = m(d, h = m(h, u = m(u, c, d, h, n[f + 5], 5, -701558691), c, d, n[f + 10], 9, 38016083), u, c, n[f + 15], 14, -660478335), h, u, n[f + 4], 20, -405537848), d = m(d, h = m(h, u = m(u, c, d, h, n[f + 9], 5, 568446438), c, d, n[f + 14], 9, -1019803690), u, c, n[f + 3], 14, -187363961), h, u, n[f + 8], 20, 1163531501), d = m(d, h = m(h, u = m(u, c, d, h, n[f + 13], 5, -1444681467), c, d, n[f + 2], 9, -51403784), u, c, n[f + 7], 14, 1735328473), h, u, n[f + 12], 20, -1926607734), d = v(d, h = v(h, u = v(u, c, d, h, n[f + 5], 4, -378558), c, d, n[f + 8], 11, -2022574463), u, c, n[f + 11], 16, 1839030562), h, u, n[f + 14], 23, -35309556), d = v(d, h = v(h, u = v(u, c, d, h, n[f + 1], 4, -1530992060), c, d, n[f + 4], 11, 1272893353), u, c, n[f + 7], 16, -155497632), h, u, n[f + 10], 23, -1094730640), d = v(d, h = v(h, u = v(u, c, d, h, n[f + 13], 4, 681279174), c, d, n[f + 0], 11, -358537222), u, c, n[f + 3], 16, -722521979), h, u, n[f + 6], 23, 76029189), d = v(d, h = v(h, u = v(u, c, d, h, n[f + 9], 4, -640364487), c, d, n[f + 12], 11, -421815835), u, c, n[f + 15], 16, 530742520), h, u, n[f + 2], 23, -995338651), d = g(d, h = g(h, u = g(u, c, d, h, n[f + 0], 6, -198630844), c, d, n[f + 7], 10, 1126891415), u, c, n[f + 14], 15, -1416354905), h, u, n[f + 5], 21, -57434055), d = g(d, h = g(h, u = g(u, c, d, h, n[f + 12], 6, 1700485571), c, d, n[f + 3], 10, -1894986606), u, c, n[f + 10], 15, -1051523), h, u, n[f + 1], 21, -2054922799), d = g(d, h = g(h, u = g(u, c, d, h, n[f + 8], 6, 1873313359), c, d, n[f + 15], 10, -30611744), u, c, n[f + 6], 15, -1560198380), h, u, n[f + 13], 21, 1309151649), d = g(d, h = g(h, u = g(u, c, d, h, n[f + 4], 6, -145523070), c, d, n[f + 11], 10, -1120210379), u, c, n[f + 2], 15, 718787259), h, u, n[f + 9], 21, -343485551),
                    u = u + y >>> 0,
                    c = c + b >>> 0,
                    d = d + x >>> 0,
                    h = h + _ >>> 0
            }
            return endian([u, c, d, h])
        }
    )._ff = function (e, t, n, i, r, o, s) {
        var a = e + (t & n | ~t & i) + (r >>> 0) + s;
        return (a << o | a >>> 32 - o) + t
    }
    ,
    a._gg = function (e, t, n, i, r, o, s) {
        var a = e + (t & i | n & ~i) + (r >>> 0) + s;
        return (a << o | a >>> 32 - o) + t
    }
    ,
    a._hh = function (e, t, n, i, r, o, s) {
        var a = e + (t ^ n ^ i) + (r >>> 0) + s;
        return (a << o | a >>> 32 - o) + t
    }
    ,
    a._ii = function (e, t, n, i, r, o, s) {
        var a = e + (n ^ (t | ~i)) + (r >>> 0) + s;
        return (a << o | a >>> 32 - o) + t
    }
    ,
    a._blocksize = 16,
    a._digestsize = 16;
    // b = function (e, t) {
    //     var n = wordsToBytes(a(e, t));
    //     return t && t.asBytes ? n : t && t.asString ? s.bytesToString(n) : bytesToHex(n)
    // }
    return  bytesToHex(wordsToBytes(a(e, t)))
}
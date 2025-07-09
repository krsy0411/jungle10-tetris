const modalKeyExplain = `
                <div class="text-[32px] font-bold text-green-500 flex gap-2 justify-center items-center">블록 이동 :
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">←</div>
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">↓</div>
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">→</div>
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">A </div>
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">S </div>
                    <div class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">D </div>
                </div>
                <div class="text-[32px] font-bold text-green-500 py-8 text-center">아래로 한번에 이동 :
                    <span class="text w-[45px] h-[45px] bg-gray-400 font-bold text-black px-5 py-1">SPACE BAR </span>
                </div>
                <div class="text-[32px] font-bold text-green-500 text-center flex justify-center items-center gap-2">블록 회전 :
                    <span class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">↑</span>
                    <span class="flex text w-[45px] h-[45px] bg-gray-400 font-bold text-black items-center justify-center">W </span>
                </div>
`
const modalFindRoom = `
    <div class="relative w-full">
            <input id="room" type="text" placeholder=" "
                class="peer w-full px-4 pt-6 pb-2 border border-gray-300 rounded-md text-base focus:outline-none focus:border-green-500" />
            <label for="room" class="absolute left-4 top-3.5 text-green-500 text-base font-bold transition-all duration-200
        peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-base
        peer-focus:top-2 peer-focus:text-sm peer-focus:text-green-500">
                방 번호
            </label>
        </div>

        <button
            class="mt-[22px] w-full py-3 bg-green-500 text-white font-bold rounded-md hover:bg-green-600 transition">
            입장 버튼
        </button>
`

